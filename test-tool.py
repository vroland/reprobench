import os
from reprobench.tools.executable import ExecutableTool
from pathlib import Path


class TestTool(ExecutableTool):
    name = "Test"
    prefix = '-'
    path = "/home/ansc921b/repobench_ng/minisat"

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

