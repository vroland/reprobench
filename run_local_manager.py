import pathlib

from reprobench.managers.local import LocalManager
import yaml
import os

path=pathlib.Path(__file__).parent.resolve()
os.chdir(path)

mconfig = None
with open(os.path.join(path,'./benchmark_system_config.yml')) as config_f:
    try:
        mconfig=yaml.safe_load(config_f)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)


m = LocalManager(num_workers=1, server_address=mconfig['server_url'], output_dir=mconfig['output'], multirun_cores=0,
                 config=mconfig['default_exp_config'], tunneling=None, repeat=mconfig['repeat'], rbdir="")

m.run()
