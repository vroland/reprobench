import os
from reprobench.tools.executable import ExecutableTool
from pathlib import Path
import subprocess
from loguru import logger


class ClaspTool(ExecutableTool):
    name = "Clasp Tool"
    prefix = '-'
    path = "/home/vagrant/src3/reprobench/dpkg/clingo/clasp"
    gringo_path = "/home/vagrant/src3/reprobench/dpkg/clingo/gringo"

    @classmethod
    def is_ready(cls):
        return Path(cls.path).is_file()

    def get_arguments(self):
        ret = []
        for key, value in self.parameters.items():
            if not value.strip() == "":
                ret.append(f"{self.prefix}{key}={value}")
            else:
                ret.append(f"{self.prefix}{key}")

        return ret

    def get_cmdline(self):
        logger.warning(self.path)
        # logger.error(*self.get_arguments())
        return [self.path, *self.get_arguments()]

    def run(self, executor):
        my_env = os.environ.copy()
        self.run_internal(executor, my_env)

    def run_internal(self, executor, environment):
        logger.debug([*self.get_cmdline(), self.task])

        executor.run(
            self.get_cmdline(),
            directory=self.cwd,
            input_str = self.task,
            out_path=self.get_out_path(),
            err_path=self.get_err_path(),
        )

class ClaspToolLibc(ClaspTool):
    def run(self, executor):
        my_env = os.environ.copy()
        my_env["GLIBC_THP_ALWAYS"] = 1
        self.run_internal(executor, my_env)
