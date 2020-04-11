import platform
import os
import glob

from loguru import logger
from playhouse.apsw_ext import CharField

from reprobench.core.base import Step
from reprobench.core.db import BaseModel
from reprobench.utils import send_event


class KernelParameters(BaseModel):
    hostname = CharField(primary_key=True)
    platform = CharField(null=True)
    transparent_hugepage = CharField(null=True)


STORE_SYSINFO = b"sysinfo:kernelparameters"


class SetupKernel(Step):
    @classmethod
    def register(cls, config=None):
        KernelParameters.create_table()

    @classmethod
    def _set_thp(cls, config):
        info = {}

        info["platform"] = platform.platform(aliased=True)

        if 'transparent_hugepage' in config:
            with open('/sys/kernel/mm/transparent_hugepage/enabled', 'r') as thp:
                logger.info(f"THP value was: {thp.readlines()}")
            logger.info('THP setting value to "%s"' % config['transparent_hugepage'])
            try:
                with open('/sys/kernel/mm/transparent_hugepage/enabled', 'w') as thp:
                    thp.write(config['transparent_hugepage'])
            except IOError as e:
                logger.error('Unable to write to file "/sys/kernel/mm/transparent_hugepage/enabled".')
                logger.error(e)
            with open('/sys/kernel/mm/transparent_hugepage/enabled', 'r') as thp:
                value = thp.readlines()
                logger.info(f"THP value is now: {value}")
                info['transparent_hugepage'] = value

        # see: Hackenberg, Schoene, Ilsche, Molka, Schuchart, Geyer: An Energy Efficiency Feature Survey of the Intel Haswell Processor (IPDPSW'2015)
        if 'governors' in config:
            driver = ''
            try:
                governor_path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_driver"
                with open(governor_path, 'r') as driver_fh:
                    driver = driver_fh.read().replace('\n','')
                    logger.info(f"Driver was {driver}")
                logger.error(driver)
                if driver == 'intel_pstate':
                    logger.debug('Checking if turbo P-states are deactivated...')
                    turbo_path='/sys/devices/system/cpu/intel_pstate/no_turbo'
                    turbo=''
                    with open(turbo_path, 'r') as turbo_fh:
                        turbo = turbo_fh.read().replace('\n','')
                    if turbo=='1':
                        logger.info('Setting turbo P-states is disallowed. (For details, see: https://www.kernel.org/doc/html/v4.12/admin-guide/pm/intel_pstate.html#turbo-p-states-support).')
                    else:
                        logger.info('Turbo value was {turbo}')
                        try:
                            with open(turbo_path, 'w') as turbo_fh:
                                turbo_fh.write('1')
                        except IOError as e:
                            logger.error('Could not set turbo value to 1 in file {turbo_path}. Probably insufficient permissions.')
                            logger.error(f'You might need to run "echo 1 | sudo  tee {turbo_path}" manually or disable it in the BIOS.')
                            raise RuntimeError('Exiting')

                    syscpu_path= '/sys/devices/system/cpu/cpu[0-9]*'
                    for cpu in sorted(glob.glob(syscpu_path)):
                        logger.debug(cpu)
                        logger.warning(f"Consider resetting the scaling_min/max_frequency after the experiment for energy saving purposes")
                        with open(f"{cpu}/cpufreq/scaling_min_freq", 'r') as min_fh:
                            minfreq=min_fh.read().replace('\n','')
                            logger.warning(f"Min was: {minfreq}. Run 'echo {minfreq} | sudo tee {min_fh.name}'")
                        with open(f"{cpu}/cpufreq/scaling_max_freq", 'r') as max_fh:
                            maxfreq=max_fh.read().replace('\n','')
                            logger.warning(f"Max was: {maxfreq}. Run 'echo {maxfreq} | sudo tee {max_fh.name}'")
                        try:
                            with open(f"{cpu}/cpufreq/scaling_min_freq", 'w') as min_fh:
                                min_fh.write(maxfreq)
                                logger.warning(f"Setting min to value: {maxfreq}")
                        except PermissionError as e:
                            val=min_fh.name.replace('cpu0','cpu*')
                            logger.error(f"Could not write scaling due to insufficient permissions. You need to run 'echo {maxfreq} | sudo tee {val}' manually.")
                            break
            except FileNotFoundError as e:
                logger.error(f"Was unable to set performance governor (file {governor_path} does not exist.")
            raise NotImplementedError

        return info

    @classmethod
    def execute(cls, context, config=None):
        hostname = platform.node()
        logger.error(config)
        info = cls._set_thp(config)
        run_id = context["run"]["id"]
        payload = dict(run_id=run_id, node=dict(hostname=hostname, **info))
        send_event(socket=context["socket"], event_type=STORE_SYSINFO, payload=payload,
                   reconnect=context['server_address'], disconnect=True)
