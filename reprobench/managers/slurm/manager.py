import math
import subprocess
import sys
from pathlib import Path

from loguru import logger

from sshtunnel import SSHTunnelForwarder
from reprobench.managers.base import BaseManager
from reprobench.utils import read_config

from .utils import to_comma_range


class SlurmManager(BaseManager):
    def __init__(self, config, server_address, tunneling, **kwargs):
        BaseManager.__init__(self, config, server_address, tunneling, **kwargs)
        self.additional = kwargs.pop("additional_args")
        self.cpu_count = kwargs.pop("reserve_cores")
        self.mem_limit = kwargs.pop("reserve_memory")
        self.time_limit = kwargs.pop("reserve_time")
        self.reserve_hosts = kwargs.pop("reserve_hosts")
        self.email = kwargs.pop("email")

    def prepare(self):
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        limits = self.config["limits"]
        time_limit_minutes = int(math.ceil(limits["time"] / 60.0))

        if self.cpu_count == 0:
            self.cpu_count = limits.get("cores", 1)

        if self.time_limit == 0:
            # @TODO improve this
            self.time_limit = 2 * time_limit_minutes

        if self.mem_limit == 0:
            if 'scheduler_memory' in limits:
                self.mem_limit = limits["scheduler_memory"]
            else:
                self.mem_limit = 0


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

    def stop(self):
        subprocess.run(["scancel", f"--name={self.config['title']}-benchmark-worker"])

    def spawn_workers(self):
        logger.info("Spawning workers...")

        address_args = f"--address={self.server_address}"
        if self.tunneling is not None:
            address_args = f"-h {self.tunneling['host']} -p {self.tunneling['port']} -K {self.tunneling['key_file']}"

        target_path = f"{sys.exec_prefix}/bin/reprobench"
        if len(self.rbdir) > 0:
            target_path = f"{self.rbdir}/reprobench-bin"

        worker_cmd = f"{target_path} worker {address_args} -vv --multirun_cores={self.multirun_cores}"
        host_limit = self.pending
        if self.multirun_cores > 0:
            host_limit = self.reserve_hosts

        worker_submit_cmd = [
            "sbatch",
            "--parsable",
            f"--array=1-{host_limit}",
            f"--time={self.time_limit}",
            f"--mem={self.mem_limit}",
            f"--cpus-per-task={self.cpu_count}",
            f"--job-name={self.config['title']}-benchmark-worker",
            f"--output={self.output_dir}/slurm-worker_%a.out",
            f"--mail-user={self.email}",
            f"--mail-type=end"
        ]

        if self.multirun_cores > 0:
            worker_submit_cmd.append("--exclusive")

        logger.error(worker_submit_cmd)

        # Additional args may contain args that are required by the scheduler
        if len(self.additional) > 0:
            additional_args = self.additional.split(" ")
            for i in range(0, len(additional_args), 2):
                # TODO: This is a hack
                if i+1 < len(additional_args) and additional_args[i].startswith("-") and not additional_args[i+1].startswith("-"):
                    worker_submit_cmd.append(f"{additional_args[i]} {additional_args[i+1]}")
                    i += 1
                else:
                    worker_submit_cmd.append(additional_args[i])
                    if i + 1 < len(additional_args):
                        worker_submit_cmd.append(additional_args[i+1])

        # Finaly add command
        worker_submit_cmd.append(f"--wrap=\"srun {worker_cmd}\"")

        logger.trace(worker_submit_cmd)
        self.worker_job = subprocess.check_output(" ".join(worker_submit_cmd), shell=True).decode().strip()
        logger.info(f"Worker job array id: {self.worker_job}")

    def wait(self):
        if self.tunneling is not None:
            self.server.stop()

