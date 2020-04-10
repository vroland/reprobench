from reprobench.core.base import Step, Observer
from reprobench.executors.events import STORE_RUNSTATS, STORE_THP_RUNSTATS

from .db import RunStatistic, RunStatisticExtended
from loguru import logger


class RunStatisticObserver(Observer):
    SUBSCRIBED_EVENTS = (STORE_RUNSTATS,)

    @classmethod
    def handle_event(cls, event_type, payload, **kwargs):
        logger.trace("Received the following payload:")
        logger.trace(payload)
        if event_type == STORE_RUNSTATS:
            RunStatistic.insert(**payload).on_conflict("replace").execute()


class RunStatisticExtendedObserver(Observer):
    SUBSCRIBED_EVENTS = (STORE_THP_RUNSTATS,)

    @classmethod
    def handle_event(cls, event_type, payload, unqlite, **kwargs):
        logger.trace("Received the following payload:")
        logger.trace(payload)

        if event_type == STORE_THP_RUNSTATS:
            logger.trace(payload)
            run_statistic = unqlite.collection('RunStatisticExtended')
            with unqlite.transaction():
                if not run_statistic.exists():
                    run_statistic.create()  # create collection
                run_statistic.store(payload)


class Executor(Step):
    def __init__(self, *args, **kwargs):
        pass

    def prerun(self):
        raise NotImplementedError

    def run(
        self,
        cmdline,
        out_path=None,
        err_path=None,
        input_str=None,
        directory=None,
        **kwargs
    ):
        raise NotImplementedError

    @classmethod
    def register(cls, config=None):
        RunStatistic.create_table()

    @classmethod
    def execute(cls, context, config=None):
        tool = context["tool"]
        executor = cls(context, config)
        tool(context).prerun(executor)
        tool(context).run(executor)
