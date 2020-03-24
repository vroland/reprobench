import atexit
import subprocess
import sys
import time
from multiprocessing import Pool, Process

from loguru import logger
from sshtunnel import SSHTunnelForwarder
from tqdm import tqdm

from reprobench.core.worker import BenchmarkWorker
from reprobench.managers.base import BaseManager


class LocalManager(BaseManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_time = None
        self.workers = []
        self.runner_process = None
        self.cluster_job_id = kwargs.get("cluster_job_id", None)
        if self.multicore is not None and self.cluster_job_id is None:
            logger.warning("*" * 120)
            logger.warning("Local runner IGNORES CORE PINNING unless you set cluster_job_id manually to -1 "
                           "using command line parameter -1.")
            logger.warning("*" * 120)

    def exit(self):
        for worker in self.workers:
            worker.terminate()
            worker.join()

        logger.info(f"Total time elapsed: {time.perf_counter() - self.start_time}")

    def prepare(self):
        atexit.register(self.exit)
        self.start_time = time.perf_counter()
        if self.tunneling is not None:
            self.server = SSHTunnelForwarder(
                self.tunneling["host"],
                remote_bind_address=("127.0.0.1", self.tunneling["port"]),
                ssh_pkey=self.tunneling["key_file"],
                ssh_config_file=self.tunneling["ssh_config_file"],
            )

            # https://github.com/pahaz/sshtunnel/issues/138
            if sys.version_info[0] > 3 or (
                sys.version_info[0] == 3 and sys.version_info[1] >= 7
            ):
                self.server.daemon_forward_servers = True

            self.server.start()
            self.server_address = f"tcp://127.0.0.1:{self.server.local_bind_port}"
            logger.info(f"Tunneling established at {self.server_address}")

    @staticmethod
    def spawn_worker(server_address, multicore=None, cluster_job_id=None):
        # TODO: This disables tunneling
        worker = BenchmarkWorker(server_address=server_address, tunneling=None, multicore=multicore,
                                 cluster_job_id=cluster_job_id)
        worker.run()

    def spawn_workers(self):
        logger.error(f"Value of cluster_job_id is {self.cluster_job_id}")
        if self.cluster_job_id is None or self.cluster_job_id == -1:
            if self.multicore and "processes" in self.multicore:
                num_workers = self.multicore['processes']
            else:
                num_workers = int(subprocess.check_output('cat /proc/cpuinfo | grep "physical id" | sort -u | wc -l',
                                                          shell=True))
            logger.info(f"Starting with {num_workers} workers.")

            self.pool = Pool(num_workers)
            jobs_address = (self.server_address for _ in range(self.num_pending))
            self.pool_iterator = self.pool.imap_unordered(self.spawn_worker, jobs_address)
            self.pool.close()
        else:
            logger.warning("*" * 120)
            logger.warning(" Cluster JobID was specified as cluster_job_id={self.cluster_job_id}. Running call similar "
                           "to cluster worker call.")
            logger.warning("*" * 120)
            logger.error("Cluster job id")
            self.runner_process = Process(target=LocalManager.spawn_worker,
                                          args=[self.server_address, self.multicore, self.cluster_job_id])
            self.runner_process.start()

    def wait(self):
        if self.cluster_job_id is None or self.cluster_job_id == -1:
            progress_bar = tqdm(desc="Executing runs", total=self.num_pending)
            for _ in self.pool_iterator:
                progress_bar.update()
            progress_bar.close()
            self.pool.join()
        else:
            logger.info("Running runner process")
            self.runner_process.join()
            logger.info("Done")

        if self.tunneling is not None:
            self.server.stop()
