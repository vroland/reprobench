from reprobench.managers.slurm.manager import SlurmManager
from loguru import logger
import sys
import yaml

mconfig = None
with open('./meta_config.yml') as config_f:
    try:
        mconfig=yaml.safe_load(config_f)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)


logger.add(sys.stderr, level="TRACE")
m = SlurmManager( num_workers=1, server_address=mconfig['server_url'], output_dir=mconfig['output'],
                 config=mconfig['config'], tunneling=None, repeat=1, rbdir="/home/jfichte/reprobench"
, reserve_cores=mconfig['reserve_cores'], reserve_memory=0, additional_args="--partition=haswell64 -A p_mcc2020 --exclusive", reserve_time=mconfig['reserve_time'],
                  reserve_hosts=mconfig['reserve_hosts'], multirun_cores=4, email=mconfig['email'], processes=mconfig['processes']
#, reserve_cores=24, reserve_memory=0, additional_args="--partition=haswell64 -A p_gpusat", reserve_time=3600, reserve_hosts=1, processes=12
                  )

m.run()
