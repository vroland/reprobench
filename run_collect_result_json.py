#!/usr/bin/env python3
import glob
import json
import os

import pandas as pd
import yaml
import zmq
from loguru import logger

from reprobench.core.bootstrap.client import bootstrap_tools
from reprobench.executors import RunSolverPerfEval
from reprobench.executors.events import STORE_THP_RUNSTATS
from reprobench.utils import read_config, encode_message

mconfig = None
with open('./meta_config.yml') as config_f:
    try:
        mconfig = yaml.safe_load(config_f)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

config = mconfig['config']
config = read_config(config, resolve_files=True)

for module in config['steps']['run']:
    if module['module'] != 'reprobench.executors.RunSolverPerfEval':
        continue
    nonzero_rte = module['config']['nonzero_rte']

# TODO: make parameter


tconfig = bootstrap_tools(config)
folders = []
for tool in tconfig:
    folders.append(os.path.abspath("./%s/%s" % (mconfig['output'], tool)))

send_events = False
conn = None
socket = None
if send_events:
    context = zmq.Context.instance()
    socket = context.socket(zmq.DEALER)
    socket.connect(mconfig['server_url'])

# hack the server and send bootstrap & sysinfo messages
# send_event(socket, RUN_START, 'payload')
# send_event(socket, BOOTSTRAP, 'payload')
#
# send_event(socket, RUN_START, 'payload')

df = None

# TODO: handling of multiple keys
keys = ['runsolver_WCTIME', 'runsolver_CPUTIME', 'runsolver_USERTIME', 'runsolver_SYSTEMTIME', 'runsolver_CPUUSAGE',
        'runsolver_MAXVM', 'runsolver_TIMEOUT', 'runsolver_MEMOUT', 'runsolver_STATUS', 'perf_dTLB_load_misses',
        'perf_dTLB_loads', 'perf_dTLB_store_misses', 'perf_dTLB_stores', 'perf_iTLB_load_misses', 'perf_iTLB_loads',
        'perf_cycles', 'perf_cache_misses', 'perf_elapsed', 'return_code', 'cpu_time', 'wall_time',
        'max_memory', 'platform', 'hostname', 'run_id', 'verdict', 'runsolver_error']

for folder in folders:
    for file in glob.glob('%s/**/result.json' % folder, recursive=True):
        my_folder = os.path.dirname(file)
        result_p = "%s/result.json" % my_folder
        with open(result_p, 'r') as result_f:
            try:
                result = json.load(result_f)
            except json.decoder.JSONDecodeError as e:
                logger.error(e)
                logger.error(result_p)
                exit(1)
            stats = RunSolverPerfEval.compile_stats(stats=result, run_id=result['run_id'], nonzero_as_rte=nonzero_rte)
            if df is None:
                # TODO: handling of missing keys and default from file
                # df = pd.DataFrame(columns=result.keys())
                df = pd.DataFrame(columns=keys)
            print(result.keys())
            cols = df.columns
            try:
                df.loc[len(df)] = stats
            except ValueError as e:
                missing = set(cols) - set(stats.keys())
                logger.info("Following keys where missing... adding na.")
                logger.info(missing)
                for e in missing:
                    stats[e] = 'NaN'
                df.loc[len(df)] = stats
        # logger.info(result)
        if send_events:
            logger.error('Send Event...')
            # send_event(socket = socket, event_type=STORE_THP_RUNSTATS, payload=result)
            #
            socket.send_multipart([STORE_THP_RUNSTATS, encode_message(result)])
            logger.error('Done...')

df.to_csv('output_%s.csv' % config['title'])
