import yaml

from reprobench.managers.condor.manager import CondorManager

mconfig = None
with open('./benchmark_system_config.yml') as config_f:
    try:
        mconfig = yaml.safe_load(config_f)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

m = CondorManager(server_address=mconfig['server_url'], output_dir=mconfig['output'],
                 config=mconfig['default_exp_config'], tunneling=None, repeat=mconfig['repeat'],
                 rbdir="/mnt/vg01/lv01/home/decodyn/reprobench", reserve_cores=mconfig['reserve_cores'], reserve_memory=0,
                 additional_args=f"",
                 reserve_time=mconfig['reserve_time'],
                 reserve_hosts=mconfig['reserve_hosts'], email=mconfig['email'],
                 multicore=mconfig['multicore']
                 # , reserve_cores=24, reserve_memory=0, additional_args="--partition=haswell64 -A p_gpusat", reserve_time=3600, reserve_hosts=1, processes=12
                 )

m.run()
