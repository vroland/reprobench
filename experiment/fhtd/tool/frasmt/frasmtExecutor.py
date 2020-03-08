import json
import os

from loguru import logger

from reprobench.executors.db import RunStatisticExtended
from reprobench.tools.executable import ExecutableTool


class FhtdTool(ExecutableTool):
    name = "SAT Tool"
    prefix = '-'
    path = "./bin/frasmt_wrapper.sh"

    ERROR_CPLEX_LICENSE = "CPLEX_L"
    ERROR_MEMOUT_ENCODING = "MEM_ENC"
    ERROR_WRONG_DECOMPOSITION = "DECOMP"
    ERROR_RECONSTRUCTING = "MODEL_REC"

    def get_arguments(self):
        return [f"{self.prefix}{key} {value}" for key, value in self.parameters.items()]

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
            input_str="-f %s" % self.task,
            out_path=self.get_out_path(),
            err_path=self.get_err_path(),
        )

    @staticmethod
    def keys():
        return ["width", 'width_frac_numerator', 'width_frac_denominator', "err", '#vertices', '#hyperedges',
                'ret_fhtd', 'size_largest_hyperedge', 'pre_clique_size', 'num_twins', 'hash', 'enc_wall', 'pre_wall',
                'verdict']

    @staticmethod
    def err_dict(verdict):
        ret = {k: "NaN" for k in FhtdTool.keys()}
        if verdict == RunStatisticExtended.SUCCESS:
            ret.update({"verdict": RunStatisticExtended.RUNTIME_ERR})
        else:
            ret.update({"verdict": verdict})
        return ret

    @staticmethod
    def evaluator(path, stats):
        fstdout = os.path.join(path, 'stdout.txt')
        fstderr = os.path.join(path, 'stderr.txt')
        verdict = stats['verdict']
        # print(verdict)
        result = FhtdTool.err_dict(verdict)
        with open(fstdout, 'r') as f:
            content = f.readlines()
            for line in content:
                if line.startswith('c '):
                    continue
                elif len(line.replace(" ", "").replace('\t', "")) == 0:
                    continue
                elif line.startswith("{"):
                    try:
                        result = json.loads(line)
                        result['ret_fhtd'] = result['solved']
                        result['width_frac_numerator'] = result['width_fractional']['numerator']
                        result['width_frac_denominator'] = result['width_fractional']['denominator']
                        # try:
                        if result["solved"] != 1 and verdict == RunStatisticExtended.SUCCESS:
                            result['verdict'] = RunStatisticExtended.RUNTIME_ERR
                        # except KeyError:
                        #     logger.error(filename)
                    except json.decoder.JSONDecodeError as e:
                        break
        with open(fstderr, 'r') as f:
            content = f.readlines()
            for line in content:
                if line.startswith('c '):
                    if "ERROR in Tree Decomposition." in line:
                        result.update({"verdict": FhtdTool.ERROR_WRONG_DECOMPOSITION})
                        break
                    continue
                if "CPLEX Error  1016: Community Edition. Problem size limits exceeded." in line:
                    result.update({"verdict": FhtdTool.ERROR_CPLEX_LICENSE})
                    break
                if "MemoryError" in line:
                    result.update({"verdict": FhtdTool.ERROR_MEMOUT_ENCODING})
                    break
                if "KeyError: 'weight" in line:
                    result.update({"verdict": FhtdTool.ERROR_RECONSTRUCTING})
                    break




        # if not result:
        #     logger.error(f"Error for file {fstdout}")
        #     logger.warning(f"Content was {''.join(content)}")
        for k in list(result.keys()):
            keys = FhtdTool.keys()
            if k not in keys:
                del result[k]
        return result
