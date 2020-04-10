from pathlib import Path

from loguru import logger

from reprobench.core.base import Tool


class ExecutableTool(Tool):
    name = "Basic Executable Tool"
    path = None
    prefix = "--"

    @classmethod
    def is_ready(cls):
        return True

    @staticmethod
    def keys():
        return []

    @staticmethod
    def evaluator(filename, stats):
        return {}

    def get_arguments(self):
        return [f"{self.prefix}{key}={value}" for key, value in self.parameters.items()]

    def get_cmdline(self):
        return [self.path, *self.get_arguments(), self.task]

    def get_out_path(self):
        return Path(self.cwd) / "run.out"

    def get_err_path(self):
        return Path(self.cwd) / "run.err"

    def get_output(self):
        return self.get_out_path().read_bytes()

    def get_error(self):
        return self.get_err_path().read_bytes()

    def prerun(self, executor):
        executor.prerun(
            self.get_cmdline(),
            directory=self.cwd,
            out_path=self.get_out_path(),
            err_path=self.get_err_path(),
        )

    def run(self, executor):
        logger.debug([*self.get_cmdline(), self.task])
        executor.run(
            self.get_cmdline(),
            directory=self.cwd,
            out_path=self.get_out_path(),
            err_path=self.get_err_path(),
            task=self.task,
            date=self.date
        )
