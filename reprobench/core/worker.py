import sys
import atexit
import json
import multiprocessing as mp
import time
from pathlib import Path
import os
from sys import platform
import threading
import subprocess

import click
import zmq
from sshtunnel import SSHTunnelForwarder, BaseSSHTunnelForwarderError
from loguru import logger

from reprobench.console.decorators import common, server_info, use_tunneling
from reprobench.core.events import (
    RUN_FINISH,
    RUN_INTERRUPT,
    RUN_START,
    RUN_STEP,
    WORKER_JOIN
)
from reprobench.utils import decode_message, import_class, send_event

REQUEST_TIMEOUT = 15000


class BenchmarkWorker:
    def __init__(self, server_address, tunneling, multirun_cores=0):
        self.server_address = server_address
        self.multirun_cores = multirun_cores
        self.isunix = (platform == "linux" or platform == "linux2")

        if tunneling is not None:
            for _ in range(1, 5):
                try:
                    self.server = SSHTunnelForwarder(
                        tunneling["host"],
                        remote_bind_address=("127.0.0.1", tunneling["port"]),
                        ssh_pkey=tunneling["key_file"],
                        ssh_config_file=tunneling["ssh_config_file"],
                    )

                    # https://github.com/pahaz/sshtunnel/issues/138
                    if sys.version_info[0] > 3 or (
                        sys.version_info[0] == 3 and sys.version_info[1] >= 7
                    ):
                        self.server.daemon_forward_servers = True

                    self.server.start()
                    self.server_address = f"tcp://127.0.0.1:{self.server.local_bind_port}"
                    logger.info(f"Tunneling established at {self.server_address}")
                    time.sleep(1)  # Let the tunnel establish
                    self.server.check_tunnels()

                    atexit.register(self.stop_tunneling)
                    return
                except (BaseSSHTunnelForwarderError, ConnectionResetError) as ee:
                    logger.info(f"Worker spawn failed {ee}")
                    time.sleep(3)
        else:
            self.server = None

    def killed(self, run_id):
        if self.socket:
            # TODO: Modify atexit events...
            send_event(self.socket, RUN_INTERRUPT, run_id)

    def stop_tunneling(self):
        self.server.stop()

    def run(self):
        # Check if socket is connected, or reconnect on demand....

        if self.multirun_cores == 0:
            self.run_internal()
        else:
            # Pin this controlling thread to the first CPU (unix only)
            if self.isunix:
                try:
                    os.sched_setaffinity(0, [0])
                except OSError as ee:
                    logger.error(f"Failed to set affinity for control thread {ee}")

            def internal_runner(t_cpu):
                logger.debug(f"Starting worker for CPU {t_cpu}")
                ret = mp.Value("b", True, lock=False)

                while ret.value:
                    ip = mp.Process(target=self.run_internal, args=[t_cpu, self.multirun_cores, ret])
                    ip.start()
                    # A timeout here could enforce a runtime limit...
                    ip.join()

                logger.debug(f"Worker for CPU {t_cpu} finished")

            # Ideally the processes should be distributed among NUMA regions. There is a python libary that provides
            # NUMA information. Since it caused errors on Taurus, it is not used here

            # Get number of physical CPUs, not cores
            numcpu = int(subprocess.check_output('cat /proc/cpuinfo | grep "physical id" | sort -u | wc -l', shell=True))
            cores_per_cpu = mp.cpu_count() // numcpu
            ppcpu = cores_per_cpu // self.multirun_cores

            runner_threads = []
            for c_cpu in range(0, numcpu):
                # Start from last core, this avoids overlap with the runner if possible
                c_idx = (c_cpu + 1) * cores_per_cpu

                for c_proc in range(0, ppcpu):
                    t = threading.Thread(target=internal_runner, args=[c_idx - self.multirun_cores])
                    runner_threads.append(t)
                    t.start()
                    # Wait to avoid parallel connections
                    c_idx -= self.multirun_cores
                    time.sleep(0.2)

            for t in runner_threads:
                try:
                    t.join()
                # If the thread is finished already, join causes a runtime exception, so this is expected behaviour
                # Checking for an active thread before would create a race condition, is the thread could finish after
                # the check, before the join.
                except RuntimeError:
                    pass
        if self.server is not None:
            self.stop_tunneling()

    def run_internal(self, target_cpu=-1, num_cores=-1, ret=None):
        # Pin process, this affects subprocesses as well
        if target_cpu > -1 and self.isunix:
            try:
                cpu_list = list(range(target_cpu, target_cpu + num_cores))
                os.sched_setaffinity(0, cpu_list)
                logger.debug(f"Pinned to CPU {cpu_list}")
            except OSError as ee:
                logger.error(f"Failed to set affinity {ee}")

        # TODO: Keeping the connection alive for the whole time is probably not ideal (especially via SSH)
        context = zmq.Context()
        socket = context.socket(zmq.DEALER)
        logger.debug(f"Connecting to {self.server_address}")
        socket.connect(self.server_address)

        send_event(socket, WORKER_JOIN)
        run = decode_message(socket.recv())

        if run is None:
            logger.info("No more tasks left, exiting...")
            if ret is not None:
                ret.value = False
            return False

        run_id = run["id"]
        # TODO: This probably needs correction
        atexit.register(self.killed, run_id)

        tool = import_class(run["tool"])

        if not tool.is_ready():
            tool.setup()

        context = {"socket": socket, "tool": tool, "run": run}
        logger.info(f"Processing task: {run['id']}")

        directory = Path(run["id"])
        directory.mkdir(parents=True, exist_ok=True)

        payload = dict(tool_version=tool.version(), run_id=run_id)
        send_event(socket, RUN_START, payload)

        for runstep in run["steps"]:
            logger.debug(f"Running step {runstep['module']}")
            step = import_class(runstep["module"])
            config = json.loads(runstep["config"])
            step.execute(context, config)
            payload = {"run_id": run_id, "step": runstep["module"]}
            send_event(socket, RUN_STEP, payload)

        send_event(socket, RUN_FINISH, run_id)
        # TODO: Probably needs changing
        atexit.unregister(self.killed)

        socket.close()

        if ret is not None:
            ret.value = True
        return True


@click.command("worker")
@click.option("--multirun_cores", type=int, default=1)
@server_info
@use_tunneling
@common
def cli(**kwargs):
    worker = BenchmarkWorker(**kwargs)
    worker.run()

if __name__ == "__main__":
    cli()
