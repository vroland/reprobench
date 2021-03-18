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

tw_runs = {}
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
            if "tw-heuristic" in sl:
                while True:
                    line = f.readline()
                    if "width = " in line:
                        w = int(line.split("=")[1])
                        line = f.readline()
                        t = int(line.split("=")[1].strip().split(" ")[0]) / 1000.0
                        results.append((w, t))
                    if line.startswith("s td") or not line:
                        break
            elif "flow_cutter_pace17" in sl:
                init_time = 0
                while True:
                    line = f.readline()
                    if line.startswith("c init_time"):
                        init_time = int(line.split(" ")[2])
                    elif line.startswith("c status"):
                        tw, t = map(int, line.split(" ")[2:])
                        t = (t - init_time) / 1000.0
                        results.append((tw, t))
                    if line.startswith("s td") or not line:
                        break

            elif "htd_main" in sl:
                init_time = 0;
                for line in f:
                    line = line.strip()
                    if line.startswith("c progress PARSING COMPLETED"):
                        init_time = int(line.split(" ")[4])
                    if line.startswith("c status"):
                        tw, t = map(int, line.split(" ")[2:])
                        t = (t - init_time) / 1000.0
                        results.append((tw, t))
                    if line.startswith("s td") or not line:
                        break

            if len(results) >= 2 and results[-1][0] == results[-2][0]:
                results.pop()
            tw_runs[file] = results;
	

with open("tw_runs.json", 'w') as payload_f:
    json.dump(tw_runs, payload_f)
