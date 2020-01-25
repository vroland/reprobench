from functools import lru_cache

from loguru import logger
from peewee import fn

from reprobench.core.base import Observer
from reprobench.core.bootstrap.server import bootstrap
from reprobench.core.db import Limit, Run, Step
from reprobench.core.events import (
    SUBMITTER_PING,
    SUBMITTER_BOOTSTRAP,
    SUBMITTER_REPORTBACK,
    RUN_FINISH,
    RUN_INTERRUPT,
    RUN_START,
    RUN_STEP,
    WORKER_JOIN,
)
from reprobench.utils import encode_message


class CoreObserver(Observer):
    SUBSCRIBED_EVENTS = (
        SUBMITTER_PING, SUBMITTER_BOOTSTRAP, SUBMITTER_BOOTSTRAP, WORKER_JOIN, RUN_START, RUN_STEP, RUN_FINISH)

    @classmethod
    @lru_cache(maxsize=1)
    def get_limits(cls):
        return {l.key: l.value for l in Limit.select()}

    @classmethod
    def get_next_pending_run(cls, cluster_job_id, pinned_host=None):
        # TODO: check for pinned_host
        try:
            if pinned_host is None:
                run = Run.get_or_none((Run.status == 0) &
                                      (Run.cluster_job_id == cluster_job_id))
            else:
                run = Run.get_or_none((Run.status == 0) &
                                      (Run.cluster_job_id == cluster_job_id) &
                                      ((Run.pinned_host == pinned_host) |
                                                (Run.pinned_host == None)))
                raise NotImplementedError("TODO:")
                # Attribute error occurs, if no open runs can be found
                # update pinned_host
                # make it work with a parameter
                # TODO: pin both to the current host
                # introduce PIN_GROUP??
                logger.error('run')
                logger.warn(run)
                logger.error(run)
                logger.error('-' * 80)

                res = Run.select()
                for x in res:
                    logger.error(x)
                # TODO: check with steps

                exit(1)

        except (Run.DoesNotExist, AttributeError):
            return None

        if run is None:
            return None

        run.status = Run.SUBMITTED
        run.save()

        last_step = run.last_step_id or 0
        # TODO: pinned_host
        # TODO: make sure here that we have only the right job_id
        # worker needs to report the job_id
        runsteps = Step.select().where(
            (Step.category == Step.RUN) & (Step.id > last_step)
        )
        limits = cls.get_limits()
        parameters = {p.key: p.value for p in run.parameter_group.parameters}

        run_dict = dict(
            id=run.id,
            task=run.task_id,
            tool=run.tool.module,
            parameters=parameters,
            steps=list(runsteps.dicts()),
            limits=limits,
        )

        return run_dict

    @classmethod
    def get_pending_runs(cls):
        last_step = (
            Step.select(fn.MAX(Step.id)).where(Step.category == Step.RUN).scalar()
        )
        Run.update(status=Run.PENDING).where(
            ((Run.status < Run.DONE) | (Run.last_step_id != last_step))
        ).execute()
        pending_runs = Run.select(Run.id).where(Run.status == Run.PENDING).count()
        return pending_runs

    @classmethod
    def update_cluster_id_for_runs(cls, old_cluster_job_id, cluster_job_id):
        logger.debug('Setting cluster_job_id for the just started jobs')
        Run.update(status=Run.PENDING, cluster_job_id=cluster_job_id).where(
            ((Run.status < Run.DONE) & (Run.cluster_job_id == old_cluster_job_id))
        ).execute()

    @classmethod
    def handle_event(cls, event_type, payload, **kwargs):
        reply = kwargs.pop("reply")
        address = kwargs.pop("address")
        server = kwargs.pop("server")

        logger.debug('Handling an event of type %s' % event_type)
        if event_type == SUBMITTER_PING:
            logger.trace('Received ping from "%s"' % address)
            logger.trace('Sending reply to "%s"' % address)
            reply.send_multipart([address, encode_message('echo reply')])
            logger.trace('Done')
        elif event_type == SUBMITTER_BOOTSTRAP:
            bootstrap(server=server, **payload)
            pending_runs = cls.get_pending_runs()
            logger.debug(payload)
            logger.debug('Sending bootstrap "%s"' % address)
            reply.send_multipart([address, encode_message(pending_runs)])
        elif event_type == SUBMITTER_REPORTBACK:
            pending_runs = cls.update_cluster_id_for_runs(**payload)
        elif event_type == WORKER_JOIN:
            run = cls.get_next_pending_run(**payload)
            reply.send_multipart([address, encode_message(run)])
        elif event_type == RUN_INTERRUPT:
            Run.update(status=Run.PENDING).where(Run.id == payload).execute()
        elif event_type == RUN_START:
            run_id = payload.pop("run_id")
            Run.update(status=Run.RUNNING, **payload).where(Run.id == run_id).execute()
        elif event_type == RUN_STEP:
            step = Step.get(module=payload["step"])
            Run.update(last_step=step).where(Run.id == payload["run_id"]).execute()
        elif event_type == RUN_FINISH:
            Run.update(status=Run.DONE).where(Run.id == payload).execute()
