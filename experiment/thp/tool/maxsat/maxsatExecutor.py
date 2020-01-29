import os
from pathlib import Path

from loguru import logger

import reprobench
from reprobench.tools.executable import ExecutableTool


class MAXSATTool(ExecutableTool):
    name = "SAT Tool"
    prefix = '-'
    path = "./bin/maxsat_solver.sh"

    @classmethod
    def is_ready(cls):
        return Path(cls.path).is_file()

    def get_arguments(self):
        return [f"{self.prefix}{key} {value}" for key, value in self.parameters.items()]

    def get_cmdline(self):
        logger.warning(self.path)
        logger.trace(self.get_arguments())
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), self.path))
        logger.trace(path)
        return [path, *self.get_arguments()]

    def run(self, executor):
        my_env = os.environ.copy()
        self.run_internal(executor, my_env)

    def run_internal(self, executor, environment):
        logger.debug([*self.get_cmdline(), self.task])

        executor.run(
            self.get_cmdline(),
            directory=self.cwd,
            input_str="-f %s" %self.task,
            out_path=self.get_out_path(),
            err_path=self.get_err_path(),
        )
