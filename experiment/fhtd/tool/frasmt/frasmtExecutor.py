import inspect
import json
import logging
import os
from pathlib import Path

from loguru import logger

import reprobench
from reprobench.executors.db import RunStatisticExtended
from reprobench.tools.executable import ExecutableTool


class FhtdTool(ExecutableTool):
    name = "SAT Tool"
    prefix = '-'
    path = "./bin/frasmt_wrapper.sh"

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
            input_str="-f %s" %self.task,
            out_path=self.get_out_path(),
            err_path=self.get_err_path(),
        )

    @staticmethod
    def keys():
        return ["width", 'width_frac_numerator', 'width_frac_denominator', "err", '#vertices', '#hyperedges',
                'ret_fhtd', 'size_largest_hyperedge',  'pre_clique_size', 'num_twins', 'hash', 'enc_wall', 'pre_wall',
                'verdict']

    @staticmethod
    def err_dict():
        ret = {k: "na" for k in FhtdTool.keys()}
        ret.update({"verdict": RunStatisticExtended.RUNTIME_ERR})
        return ret

    @staticmethod
    def evaluator(filename):
        result = FhtdTool.err_dict()
        with open(filename, 'r') as f:
            content = f.readlines()
            for line in content:
                if line.startswith('c '):
                    continue
                elif len(line.replace(" ", "").replace('\t',"")) == 0:
                    continue
                elif line.startswith("{"):
                    try:
                        result = json.loads(line)
                        result['ret_fhtd'] = result['solved']
                        result['width_frac_numerator'] = result['width_fractional']['numerator']
                        result['width_frac_denominator'] = result['width_fractional']['denominator']
                        # try:
                        if result["solved"] != '1' and 'verdict' in result and \
                            result['verdict'] != RunStatisticExtended.SUCCESS:
                            result['verdict'] = RunStatisticExtended.RUNTIME_ERR
                        # except KeyError:
                        #     logger.error(filename)
                    except json.decoder.JSONDecodeError as e:
                        break
            if not result:
                logger.error(f"Error for file {filename}")
                logger.warning(f"Content was {''.join(content)}")
            for k in list(result.keys()):
                keys = FhtdTool.keys()
                if k not in keys:
                    del result[k]
        return result
