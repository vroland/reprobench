#!/usr/bin/env python3
import glob
import json
import os
import re

import yaml

from reprobench.core.bootstrap.client import bootstrap_tools
from reprobench.executors import RunSolverPerfEval
from reprobench.utils import read_config

mconfig = None
with open('./benchmark_system_config.yml') as config_f:
    try:
        mconfig = yaml.safe_load(config_f)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

config = mconfig['default_exp_config']
config = read_config(config, resolve_files=True)

# TODO: consider tasks only
# print(bootstrap_tasks(config))

tconfig = bootstrap_tools(config)
nonzero_rte = None
for module in config['steps']['run']:
    if module['module'] != 'reprobench.executors.RunSolverPerfEval':
        continue
    nonzero_rte = module['config']['nonzero_rte']

folders = []
for tool in tconfig:
    folders.append(os.path.abspath("./output/%s" % tool))

# overwrite = False
overwrite = True
verify = True

failed = []

td_first_chars = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "s", "c", "b")
for folder in folders:
    for file in glob.glob('%s/**/stdout.txt' % folder, recursive=True):
        my_folder = os.path.dirname(file)
        payload_p, perflog, stderr_p, stdout_p, varfile, watcher, runparameters_p = RunSolverPerfEval.log_paths(
            my_folder)
        with open(file) as f:
            # tamaki
            results = []
            f.readline()
            sl = f.readline()
            print(file)
            while True:
                line = f.readline()
                if line == "":
                    print ("file ended before decomposition :(")
                    failed.append(file)
                    break
                if line.startswith("s td"):
                    decomposition = line
                    decomposition += f.read()
                    decomposition = decomposition.replace("Solver finished with exit code=143\n", "")
                    decomposition = decomposition.replace("Solver finished with exit code=0\n", "")
                    if verify:
                        for i, l in enumerate(decomposition.split("\n")):
                            if l == "":
                                continue
                            assert (l.startswith(td_first_chars)), f"wrong line start in {i}: {l}" 
                    with open(my_folder + "/decomposition.td", "w") as df:
                        # fix up jumpled solver output
                        df.write(decomposition)
                    break
print (len(failed), "failed.")
with open("twextract_failed", "w") as ff:
    ff.writelines(failed)
