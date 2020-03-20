import os

from loguru import logger

from reprobench.tools.executable import ExecutableTool


class WMCPreprocessor(ExecutableTool):
    name = "(W)MC Preprocessor"
    prefix = '-'
    path = "./pre/wmc_pre.sh"
    #TODO: run preprocessor first and report preprocessing time separatley

    def get_arguments(self):
        ret = []
        preprocessor = None
        for key, value in self.parameters.items():
            if key == 'p':
                preprocessor = value
            ret.append(f"{self.prefix}{key} {value}")
        ret.append(f"-o {self.task}.{preprocessor}")
        return ret

    def get_cmdline(self):
        logger.warning(self.get_path())
        logger.trace(self.get_arguments())
        return [self.get_path(), *self.get_arguments()]

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
