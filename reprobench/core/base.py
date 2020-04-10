import inspect
import os
from pathlib import Path

from loguru import logger

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
    def handle_event(cls, event_type, payload, unqlite, **kwargs):
        logger.debug(event_type)
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
        self.tool_name = context["tool_name"]
        self.date = context["run"]["date"]

    def prerun(self, executor):
        raise NotImplementedError

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
        return Path(cls.path).is_file() #and os.access(self.get_path, os.X_OK)

    @classmethod
    def teardown(cls):
        pass

    def get_path(self):
        if self.path.startswith("~"):
            return os.path.expanduser(self.path)
        else:
            runtm_path = os.path.join(os.path.dirname(inspect.getfile(self.__class__)), self.path)
            if os.path.islink(runtm_path):
                return os.path.abspath(runtm_path)
            else:
                return os.path.relpath(runtm_path)
