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
    def _set_thp(cls,config):
        info = {}

        info["platform"] = platform.platform(aliased=True)

        if 'transparent_hugepage' in config:
            logger.info('THP value was:')
            with open('/sys/kernel/mm/transparent_hugepage/enabled', 'r') as thp:
                logger.info(thp.readlines())
            logger.info('THP setting value to "%s"' % config['transparent_hugepage'])
            try:
                with open('/sys/kernel/mm/transparent_hugepage/enabled', 'w') as thp:
                    thp.write(config['transparent_hugepage'])
            except IOError as e:
                logger.error('Unable to write to file "/sys/kernel/mm/transparent_hugepage/enabled".')
                logger.error(e)
            logger.info('THP value is now:')
            with open('/sys/kernel/mm/transparent_hugepage/enabled', 'r') as thp:
                value = thp.readlines()
                logger.info(value)
                info['transparent_hugepage']=value

        return info

    @classmethod
    def execute(cls, context, config=None):
        hostname = platform.node()
        logger.error(config)
        info = cls._set_thp(config)
        run_id = context["run"]["id"]
        payload = dict(run_id=run_id, node=dict(hostname=hostname, **info))
        send_event(context["socket"], STORE_SYSINFO, payload)
