from reprobench.managers.slurm.manager import SlurmManager
from loguru import logger
import sys

logger.add(sys.stderr, level="TRACE")
m = SlurmManager( num_workers=1, server_address="tcp://172.26.62.66:31313", output_dir="output",
                 config="./benchmark-clasp.yml", tunneling=None, repeat=1, rbdir="/home/jfichte/reprobench"
, reserve_cores=0, reserve_memory=0, additional_args="--partition=haswell64 -A p_gpusat", reserve_time=0, reserve_hosts=1, processes=1
#, reserve_cores=24, reserve_memory=0, additional_args="--partition=haswell64 -A p_gpusat", reserve_time=3600, reserve_hosts=1, processes=12
                  )

m.run()
