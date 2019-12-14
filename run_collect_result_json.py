#!/usr/bin/env python3
import glob
import json
import os
import zmq

import yaml
from loguru import logger

from reprobench.core.bootstrap.client import bootstrap_tools
from reprobench.utils import read_config, send_event, encode_message
from reprobench.executors.events import STORE_THP_RUNSTATS
from reprobench.core.events import RUN_START

mconfig = None
with open('./meta_config.yml') as config_f:
    try:
        mconfig = yaml.safe_load(config_f)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

config = mconfig['config']
config = read_config(config, resolve_files=True)

# TODO: make parameter


tconfig = bootstrap_tools(config)
folders = []
for tool in tconfig:
    folders.append(os.path.abspath("./%s/%s" % (mconfig['output'], tool)))

send_events = True
conn = None
socket = None
if send_events:
    context = zmq.Context.instance()
    socket = context.socket(zmq.DEALER)
    socket.connect(mconfig['server_url'])

# hack the server and send bootstrap & sysinfo messages
#send_event(socket, RUN_START, 'payload')
#send_event(socket, BOOTSTRAP, 'payload')
#
# send_event(socket, RUN_START, 'payload')


for folder in folders:
    for file in glob.glob('%s/**/perflog.txt' % folder, recursive=True):
        my_folder = os.path.dirname(file)
        result_p = "%s/result.json" % my_folder
        print(result_p)
        with open(result_p, 'r') as result_f:
            result = json.load(result_f)
        logger.info(result)

        if send_events:
            logger.error('Send Event...')
            # send_event(socket = socket, event_type=STORE_THP_RUNSTATS, payload=result)
            #
            socket.send_multipart([STORE_THP_RUNSTATS, encode_message(result)])
            logger.error('Done...')

        # exit(1)
        # safe stats
