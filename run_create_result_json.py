#!/usr/bin/env python3
from reprobench.utils import decode_message, read_config, send_event
from reprobench.core.bootstrap.client import bootstrap_tasks, bootstrap_tools
import glob
import os
from reprobench.executors import RunSolverPerfEval
from loguru import logger

config = './benchmark_thp_sat.yml'
config = read_config(config, resolve_files=True)

# TODO: consider tasks only
# print(bootstrap_tasks(config))

tconfig = bootstrap_tools(config)
nonzero_rte = None
for module in config['steps']['run']:
    if module['module'] != 'reprobench.executors.RunSolverPerfEval':
        continue
    nonzero_rte=module['config']['nonzero_rte']

folders = []
for tool in tconfig:
    folders.append(os.path.abspath("./output/%s" %tool))


for folder in folders:
    for file in glob.glob('%s/**/perflog.txt' %folder, recursive=True):
        my_folder = os.path.dirname(file)
        print(my_folder)
        payload_p, perflog, stderr_p, stdout_p, varfile, watcher = RunSolverPerfEval.log_paths(my_folder)
        stats = RunSolverPerfEval.parse_logs(perflog, varfile, watcher)

        #Save payload
        #TODO: next safe payload somehow
        #make sure that run_id is saved somewhere
        payload = RunSolverPerfEval.compile_stats(stats=stats,run_id=1, nonzero_as_rte=nonzero_rte)

        logger.error(payload)

        print(payload_p)
        exit(1)
        #safe stats
        with open(payload_p, 'w') as payload_f:
            payload_f.write(json.dumps(payload))

        #re analyze stats

        print(stats)
        exit(1)


        # print(file)
