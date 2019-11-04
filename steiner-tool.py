import os
from reprobench.tools.executable import ExecutableTool
from pathlib import Path
from loguru import logger


class WataTool(ExecutableTool):
    name = "wata"
    prefix = '-'
    path = "/home1/aschidler/track1"

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
        logger.debug([*self.get_cmdline(), self.task])
        f = open(self.task, "rb")
        enc = f.read()
        f.close()

        executor.run(
            self.get_cmdline(),
            directory=self.cwd,
            input_str = enc,
            out_path=self.get_out_path(),
            err_path=self.get_err_path(),
        )

class TuwTool(ExecutableTool):
    name = "tuw"
    prefix = "-"
    path = "/home1/aschidler/pace17/steiner/benchmark_runner.py"

    def get_arguments(self):
        ret = []
        for key, value in self.parameters.items():
            if not value.strip() == "":
                ret.append(f"{self.prefix}{key}={value}")
            else:
                ret.append(f"{self.prefix}{key}")

        return ret

    def get_cmdline(self):
        return ["/usr/bin/python2.7", self.path, *self.get_arguments(), self.task]

    def run(self, executor):
        logger.debug([*self.get_cmdline(), self.task])
        f = open(self.task, "rb")
        enc = f.read()
        f.close()

        executor.run(
            self.get_cmdline(),
            directory=self.cwd,
            input_str = enc,
            out_path=self.get_out_path(),
            err_path=self.get_err_path(),
        )

