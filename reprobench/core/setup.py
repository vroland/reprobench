import platform

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
                    driver = driver_fh.read()
                    logger.info(f"Driver was {driver}")
                logger.error(driver)
                exit(1)
            except FileNotFoundError as e:
                logger.error(f"Was unable to set performance governor (file {governor_path} does not exist.")
            pass

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
