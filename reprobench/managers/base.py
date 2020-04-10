import os

import zmq
from loguru import logger

from reprobench.core.bootstrap import bootstrap_client
from reprobench.core.events import SUBMITTER_BOOTSTRAP, SUBMITTER_PING
from reprobench.utils import decode_message, read_config, send_event


class BaseManager(object):
    def __init__(self, config, server_address, tunneling, **kwargs):
        self.server_address = server_address
        self.tunneling = tunneling
        self.config = read_config(config, resolve_files=True)
        self.output_dir = kwargs.pop("output_dir")
        self.repeat = kwargs.pop("repeat")
        self.rbdir = kwargs.pop("rbdir")
        self.multicore = kwargs.pop("multicore")
        self.cluster_job_id = None
        self.num_pending = None

        context = zmq.Context()
        self.socket = context.socket(zmq.DEALER)

        self.socket.connect(self.server_address)

    def prepare(self):
        pass

    def spawn_workers(self):
        raise NotImplementedError

    def bootstrap(self):
        client_results = bootstrap_client(self.config)
        bootstrapped_config = {**self.config, **client_results}

        logger.info(f"Sending bootstrap event to server {self.server_address}")
        # TODO:
        # we have to update the initial cluster id here, simply because we know the id from the cluster scheduler....
        payload = dict(
            config=bootstrapped_config, output_dir=self.output_dir,
            repeat=self.repeat, cluster_job_id=self.cluster_job_id, overwrite=True
        )
        send_event(self.socket, SUBMITTER_BOOTSTRAP, payload)
        self.num_pending = decode_message(self.socket.recv())

    def report_back(self):
        pass

    def wait(self):
        pass

    def stop(self):
        pass

    def ping_server(self):
        logger.info('Pinging Server')
        send_event(self.socket, SUBMITTER_PING, {})
        # we are actually not really interested in the result here,
        # just that there is some response
        logger.info('Waiting for response...')
        recv = decode_message(self.socket.recv())
        logger.info('Received the following reply: "%s". Good to go...' % recv)

    def report_back(self):
        pass

    def run(self):
        self.prepare()
        self.ping_server()
        self.bootstrap()
        self.spawn_workers()
        self.report_back()
        self.wait()
