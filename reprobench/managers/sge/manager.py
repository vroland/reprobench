from sshtunnel import SSHTunnelForwarder
from reprobench.managers.base import BaseManager
from pathlib import Path
from loguru import logger

import sys
import subprocess
import math
import time
import os


class SgeManager(BaseManager):
    """A manager that uses the Sun Grid Engine."""

    def prepare(self):
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        limits = self.config["limits"]
        time_limit_minutes = int(math.ceil(limits["time"] / 60.0))

        self.cpu_count = limits.get("cores", 1)
        # @TODO improve this
        self.time_limit = 2 * time_limit_minutes
        self.mem_limit = 2 * limits["memory"]

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
        subprocess.run(["qdel", f"{self.config['title']}-benchmark-worker"])

    def spawn_workers(self):
        logger.info("Spawning workers...")

        address_args = f"--address={self.server_address}"
        if self.tunneling is not None:
            address_args = f"-h {self.tunneling['host']} -p {self.tunneling['port']} -K {self.tunneling['key_file']}"

        worker_cmd = f"{self.rbdir}/bin/reprobench worker {address_args} -vv"

        # Create submission script
        # TODO: Is it ok to assume /bin/sh?
        # TODO: Is it ok to simply erase previous file?
        sge_script = open('sge.sh', 'w')
        sge_script.writelines(["#!/bin/sh\n", worker_cmd])
        sge_script.close()

        worker_submit_cmd = [
            "qsub",
            "-r y",
            # Creates the output in the output dir
            f"-wd {self.output_dir}",
            f"-t 1-{self.pending}:1",
            # Convert to HH:MM:SS format
            f"-l h_rt={time.strftime('%H:%M:%S', time.gmtime(self.time_limit * 60))}",
            # Convert to Gigabyte
            f"-l h_vmem={'{0:.2g}G'.format(float(self.mem_limit)/1024)}",
            f"-N {self.config['title']}-benchmark-worker",
            f"{os.path.join(os.getcwd(), 'sge.sh')}",
        ]

        # TODO: Add possibility to get $TMPDIR to executing script...

        # If more than one processor, activate multiprocessor environment
        if self.cpu_count > 1:
            worker_submit_cmd.insert(6, f"-pe smp {self.cpu_count}")

        # TODO: P allows to set a project name
        logger.trace(worker_submit_cmd)
        self.worker_job = subprocess.check_output(worker_submit_cmd).decode().strip()
        logger.info(f"Worker job array id: {self.worker_job}")

    def wait(self):
        if self.tunneling is not None:
            self.server.stop()

