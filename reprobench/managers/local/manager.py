import atexit
import time
import sys
from multiprocessing import Pool, Process

from sshtunnel import SSHTunnelForwarder
from loguru import logger
from tqdm import tqdm

from reprobench.core.worker import BenchmarkWorker
from reprobench.managers.base import BaseManager


class LocalManager(BaseManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.num_workers = kwargs.pop("num_workers")
        self.start_time = None
        self.workers = []
        self.runner_process = None

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
    def spawn_worker(server_address, multirun_cores=0):
        # TODO: This disables tunneling
        worker = BenchmarkWorker(server_address, None, multirun_cores=multirun_cores)
        worker.run()

    def spawn_workers(self):
        if self.multirun_cores == 0:
            self.pool = Pool(self.num_workers)
            jobs_address = (self.server_address for _ in range(self.pending))
            self.pool_iterator = self.pool.imap_unordered(self.spawn_worker, jobs_address)
            self.pool.close()
        else:
            self.runner_process = Process(target=LocalManager.spawn_worker, args=[self.server_address, self.multirun_cores])
            self.runner_process.start()

    def wait(self):
        if self.multirun_cores == 0:
            progress_bar = tqdm(desc="Executing runs", total=self.pending)
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
