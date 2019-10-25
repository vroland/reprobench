import os
from reprobench.tools.executable import ExecutableTool
from pathlib import Path
import subprocess
from loguru import logger


class ClaspTool(ExecutableTool):
    name = "Clasp Tool"
    prefix = '-'
    path = "/home/aschidler/Downloads/clasp_glibc"
    gringo_path = "/home/aschidler/Downloads/clingo-5.4.0-linux-x86_64/gringo"

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
        return [self.path, *self.get_arguments()]

    def run(self, executor):
        my_env = os.environ.copy()
        self.run_internal(executor, my_env)

    def run_internal(self, executor, environment):
        logger.debug([*self.get_cmdline(), self.task])

        encoding_file = os.path.join(os.path.dirname(os.path.abspath(self.task)), "encoding.asp")

        process = subprocess.Popen([self.gringo_path, self.task, encoding_file], stdout=subprocess.PIPE)
        out, err = process.communicate()

        logger.debug(f"Gringo finished (Error: {err})")

        executor.run(
            self.get_cmdline(),
            directory=self.cwd,
            input_str=out,
            out_path=self.get_out_path(),
            err_path=self.get_err_path(),
            env=environment
        )


class ClaspToolLibc(ClaspTool):
    def run(self, executor):
        my_env = os.environ.copy()
        my_env["GLIBC_THP_ALWAYS"] = 1
        self.run_internal(executor, my_env)
