from loguru import logger

from reprobench.utils import recv_event

try:
    import zmq.green as zmq
except ImportError:
    pass


class Observer:
    SUBSCRIBED_EVENTS = []

    @classmethod
    def observe(cls, server):
        logger.debug(cls)

        server.observers.append(cls)

    @classmethod
    def handle_event(cls, event_type, payload, **kwargs):
        pass


class Step:
    @classmethod
    def register(cls, config=None):
        pass

    @classmethod
    def execute(cls, context, config=None):
        pass


class Tool:
    name = "Base Tool"

    def __init__(self, context):
        self.cwd = context["run"]["id"]
        self.parameters = context["run"]["parameters"]
        self.task = context["run"]["task"]

    def run(self, executor):
        raise NotImplementedError

    def get_output(self):
        raise NotImplementedError

    def get_error(self):
        raise NotImplementedError

    @classmethod
    def setup(cls):
        pass

    @classmethod
    def version(cls):
        return "1.0.0"

    @classmethod
    def is_ready(cls):
        pass

    @classmethod
    def teardown(cls):
        pass
