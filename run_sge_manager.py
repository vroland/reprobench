from reprobench.managers.sge.manager import SgeManager
from loguru import logger
import sys

logger.add(sys.stderr, level="TRACE")
m = SgeManager( num_workers=1, server_address="tcp://behemoth.ac.tuwien.ac.at:31313", output_dir="/home1/aschidler/reprobench", config="./benchmark-steiner.yml", tunneling={'host': 'behemoth', 'key_file': '/home1/aschidler/.ssh/id_rsa', 'port': 31313, 'ssh_config_file': '/home1/aschidler/.ssh/config'}, repeat=1, rbdir="/home1/aschidler/reprobench2", processes = 1, additional_args="-l bc4")
#~/.local/bin/reprobench manage sge run -h behemoth -K /home1/aschidler/.ssh/id_rsa -d /home1/aschidler/reprobench/htd/output --rbdir /home1/aschidler/.local/

m.run()
