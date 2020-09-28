#!/usr/bin/env python3
import glob
import importlib
import json
import os
import pathlib

import pandas as pd
import yaml
import zmq
from loguru import logger

from reprobench.core.bootstrap.client import bootstrap_tools
from reprobench.executors import RunSolverPerfEval
from reprobench.executors.db import RunStatisticExtended
from reprobench.executors.events import STORE_THP_RUNSTATS
from reprobench.utils import read_config, encode_message, import_class


mconfig = None
with open('./benchmark_system_config.yml') as config_f:
    try:
        mconfig = yaml.safe_load(config_f)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

config = mconfig['default_exp_config']
config = read_config(config, resolve_files=True)

nonzero_rte = None
module = None
for module in config['steps']['run']:
    if module['module'] != 'reprobench.executors.RunSolverPerfEval':
        continue
    nonzero_rte = module['config']['nonzero_rte']

if module is None or nonzero_rte is None:
    raise RuntimeError

tools = {}
i = 0
for item in config['runs']:
    module = import_class(config['tools'][item]['module'])
    tools[item] = module
    if i>0:
        print("Supports only one tool atm. Check your config. Exiting...")
        exit(1)
    i+=1



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
# send_event(socket, SUBMITTER_BOOTSTRAP, 'payload')
#
# send_event(socket, RUN_START, 'payload')

df = None

# TODO: handling of multiple keys
add_keys = ["platform", "hostname", "run_id"]
for folder in folders:
    for file in glob.glob('%s/**/result.json' % folder, recursive=True):
        my_folder = os.path.dirname(file)
        result_p = f"{my_folder}/result.json"
        cols = set(RunSolverPerfEval.keys() + module.keys() + add_keys)
        with open(f"{my_folder}/run.json", 'r') as run_f:
            run_info = json.load(run_f)
        try:
            run_id = run_info['run_id']
        except KeyError:
            run_id = os.path.dirname(result_f.name).replace(str(pathlib.Path(__file__).parent.absolute()) + '/', '')

        df_keys = set(RunSolverPerfEval.keys() + module.keys());
        with open(result_p, 'r') as result_f:
            if df is None:
                df = pd.DataFrame(df_keys)
            try:
                result = json.load(result_f)
                if not 'run_id' in result:
                    raise KeyError
            except (json.decoder.JSONDecodeError, KeyError) as e:
                #TODO: refactor
                logger.error(e)
                logger.error(f"Instance {run_id} did not finish properly.")
                stats = {'verdict': RunStatisticExtended.RUNTIME_ERR, 'run_id': run_id, 'return_code': '9'}
                for e in set(cols) - set(stats.keys()) - {"hostname"}:
                    stats[e] = 'NaN'
                stats['hostname'] = 'unknown'
                df.loc[len(df)] = stats
                continue
            #TODO: continue here
            stats = RunSolverPerfEval.compile_stats(stats=result, run_id=run_id, nonzero_as_rte=nonzero_rte)
            # TODO: after updating to non-sql database move things

            problem_stats = module.evaluator(os.path.dirname(file), stats)
            stats.update(problem_stats)

            # project to used keys only
            stats =  {k : v for k,v in stats.items() if k in df_keys}
            missing = df_keys - set(stats.keys())
            if missing:
                logger.info(f"Missing keys ({missing}) for instance {run_id} adding na.")
            df.append(stats, ignore_index=True)

        # logger.info(result)
        if send_events:
            logger.error('Send Event...')
            # send_event(socket = socket, event_type=STORE_THP_RUNSTATS, payload=result)
            #
            socket.send_multipart([STORE_THP_RUNSTATS, encode_message(result)])
            logger.error('Done...')

df.to_csv('output_%s.csv' % config['title'])
