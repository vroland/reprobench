#!/usr/bin/env python3
import glob
import json
import os
import re
import sys

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

for folder in folders:
    for file in glob.glob('%s/**/stdout.txt' % folder, recursive=True):
        my_folder = os.path.dirname(file)
        payload_p, perflog, stderr_p, stdout_p, varfile, watcher, runparameters_p = RunSolverPerfEval.log_paths(
            my_folder)

        solve_time = 0
        with open(file) as f:
            text = f.read()
            m = re.findall("^\s*,\"Solving\":\s([0-9.]*)$", text, flags=re.MULTILINE)
            # multiple matches?
            if len(m) > 1:
                print("invalid stdout file.")
                sys.exit(1)
 
            if m:
                solve_time = float(m[0])

        #if os.path.exists(payload_p) and not overwrite:
        #    continue

        stats = RunSolverPerfEval.parse_logs(perflog, varfile, watcher, stdout_p)
        # Save payload
        # TODO: next safe payload somehow
        # make sure that run_id is saved somewhere
        run_id = re.sub("%s/" % os.path.abspath(""), '', "/".join(file.split("/")[:-1]))
        payload = RunSolverPerfEval.compile_stats(stats=stats, run_id=run_id, nonzero_as_rte=nonzero_rte)

        payload["solve_time_reported"] = solve_time
        # safe stats
        with open(payload_p, 'w') as payload_f:
            payload_f.write(json.dumps(payload))
