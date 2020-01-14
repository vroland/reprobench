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
with open('./meta_config.yml') as config_f:
    try:
        mconfig = yaml.safe_load(config_f)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

config = mconfig['config']
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

overwrite = False

for folder in folders:
    for file in glob.glob('%s/**/stdout.txt' % folder, recursive=True):
        my_folder = os.path.dirname(file)
        payload_p, perflog, stderr_p, stdout_p, varfile, watcher, runparameters_p = RunSolverPerfEval.log_paths(
            my_folder)
        if os.path.exists(payload_p) and not overwrite:
            continue
        stats = RunSolverPerfEval.parse_logs(perflog, varfile, watcher)
        # Save payload
        # TODO: next safe payload somehow
        # make sure that run_id is saved somewhere
        run_id = re.sub("%s/" % os.path.abspath(""), '', file)
        payload = RunSolverPerfEval.compile_stats(stats=stats, run_id=run_id, nonzero_as_rte=nonzero_rte)

        # safe stats
        with open(payload_p, 'w') as payload_f:
            payload_f.write(json.dumps(payload))
