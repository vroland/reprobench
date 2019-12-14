from reprobench.managers.local import LocalManager
import yaml

mconfig = None
with open('./meta_config.yml') as config_f:
    try:
        mconfig=yaml.safe_load(config_f)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

m = LocalManager(num_workers=1, server_address=mconfig['server_url'], output_dir=mconfig['output'], multirun_cores=0,
                 config=mconfig['config'], tunneling=None, repeat=1, rbdir="")

m.run()
