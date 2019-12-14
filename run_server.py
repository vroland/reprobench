from reprobench.core.server import BenchmarkServer
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


print(mconfig['server_url'])

logger.add(sys.stderr, level="TRACE")
s = BenchmarkServer(mconfig['server_url'], verbosity=2)

s.run()


