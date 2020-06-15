import json
import math
import random
import subprocess
import sys
import urllib
from pathlib import Path

from loguru import logger
from sshtunnel import SSHTunnelForwarder

from reprobench.core.events import SUBMITTER_REPORTBACK
from reprobench.managers.base import BaseManager
from reprobench.utils import send_event

from jinja2 import Template
import re

class CondorManager(BaseManager):
    def __init__(self, config, server_address, tunneling, **kwargs):
        BaseManager.__init__(self, config, server_address, tunneling, **kwargs)
        self.additional = kwargs.pop("additional_args")
        self.mem_limit = kwargs.pop("reserve_memory")
        self.time_limit = kwargs.pop("reserve_time")
        self.reserve_hosts = kwargs.get("reserve_hosts", 1)
        self.email = kwargs.pop("email")
        self.slurm_job_id = None
        self.cluster_job_id = None
        # TODO: fix debuglevel, exclusive as configurable parameters
        self.debug = True
        self.exclusive = True

        self.cpus_per_task = kwargs.pop("reserve_cores", 4)

    def prepare(self):
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        limits = self.config["limits"]
        time_limit_minutes = int(math.ceil(float(limits["time"]) / 60.0))

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
        subprocess.run(["condor_rm", f"jfichte"])

    def spawn_workers(self):
        logger.info("Generating worker templates...")

        target_path = f"{sys.exec_prefix}/bin/reprobench"
        if len(self.rbdir) > 0:
            target_path = f"{self.rbdir}/reprobench-bin"
        
        address_args = f"--address={self.server_address}"
        if self.tunneling is not None:
            address_args = f"-h {self.tunneling['host']} -p {self.tunneling['port']} -K {self.tunneling['key_file']}"

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # PREPARE PARAMETERS FOR WORKER
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        multicore_str = urllib.parse.quote(json.dumps(self.multicore))
        # TODO: change to human readable

        worker_cmd = f"worker {address_args} --multicore={multicore_str}"  # {self.multicore}
        if self.debug:
            worker_cmd += " -vv"

        worker_submit_cmd = []
        # Additional args may contain args that are required by the scheduler
        if len(self.additional) > 0:
            additional_args = self.additional.split(" ")
            for i in range(0, len(additional_args), 2):
                # TODO: This is a hack
                if i + 1 < len(additional_args) and additional_args[i].startswith("-") and not additional_args[i + 1].startswith("-"):
                    worker_submit_cmd.append(f"{additional_args[i]} {additional_args[i + 1]}")
                    i += 1
                else:
                    worker_submit_cmd.append(additional_args[i])
                    if i + 1 < len(additional_args):
                        worker_submit_cmd.append(additional_args[i + 1])


        logger.info(f"{worker_cmd}")
        
        # Construct Condor Job Script File
        hosts=list(range(int(f"{self.reserve_hosts}")))
        with open(f"{self.rbdir}/output/condor_job_{self.config['title']}", "w") as condorsubmitfile:
            with open(Path(__file__).parent / "condor.submit") as template:
                t = Template(template.read())
                condorsubmitfile.write(
                    t.render(cmd=f"{target_path}", hosts=hosts, timeout=self.time_limit,rbdir=self.rbdir,args=f"{worker_cmd}",
                             memout=self.mem_limit, initialdir=f"{self.rbdir}/"))
        worker_submit_cmd = [
            f"/usr/bin/condor_submit",
            f"{self.rbdir}/output/condor_job_{self.config['title']}"
        ]

        logger.info(f"Submit command: {worker_submit_cmd}")

        #Submit to cluster scheduler and report back the JobID
        res = subprocess.check_output(" ".join(worker_submit_cmd), shell=True).decode()
        regex_str = "[0-9]+\sjob\(s\)\ssubmitted\sto\scluster\s(?P<jobid>[0-9]+)\."
        regex = re.compile(regex_str)
        self.slurm_job_id = None
        for line in res.split('\n'):
            if line.startswith("Submitting job(s)."):
                continue
            find = regex.findall(line)
            if len(find)>0:
                self.slurm_job_id = find[0]
                break
        if self.slurm_job_id is None:
            raise RuntimeError("An Error occured while submitting the job with condor")
        logger.info(f"Worker CONDOR_JOB_ID: {self.slurm_job_id}")

    def get_initial_cluster_id(self):
        self.cluster_job_id = random.randint(0, 65536)
        return self.cluster_job_id

    def report_back(self):
        send_event(self.socket, SUBMITTER_REPORTBACK,
                   dict(old_cluster_job_id=self.cluster_job_id, cluster_job_id=self.slurm_job_id))

    def wait(self):
        if self.tunneling is not None:
            self.server.stop()
