import os
from pathlib import Path

from loguru import logger

import reprobench
from reprobench.tools.executable import ExecutableTool


class ClaspASPTool(ExecutableTool):
    name = "Clasp ASP Tool"
    prefix = '-'
    path = "/home/vagrant/src3/reprobench/tools/clasp/clasp_asp.sh"

    @classmethod
    def is_ready(cls):
        return Path(cls.path).is_file()

    def get_arguments(self):
        reprobench_path = os.path.abspath(os.path.join(os.path.dirname(reprobench.__file__), '..'))
        ret = ["%s/%s" % (reprobench_path, self.parameters.get("encoding"))]
        # logger.error(self.task)
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
            input_str=self.task,
            out_path=self.get_out_path(),
            err_path=self.get_err_path(),
        )


class ClaspASPToolLibc(ClaspASPTool):
    name = "Clasp THP Tool"

    def run(self, executor):
        my_env = os.environ.copy()
        my_env["GLIBC_THP_ALWAYS"] = 1
        self.run_internal(executor, my_env)


class ClaspTool(ClaspASPTool):
    name = "Clasp Tool"
    prefix = '-'
    path = "/home/vagrant/src3/reprobench/tools/clasp/clasp_lparse.sh"

    def get_arguments(self):
        return [f"{self.prefix}{key}={value}" for key, value in self.parameters.items()]
