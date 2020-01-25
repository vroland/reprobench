#!/usr/bin/env python
import argparse

import reprobench.core.worker as worker

parser = argparse.ArgumentParser(description='%(prog)s -r remoteid:port -i cluster_job_id')
parser.add_argument('-i', '--cluster_job_id', dest='cluster_job_id', action='store',
                    default=-1, help='Set cluster_job_id [default=-1]')
parser.add_argument('-r', '--remote-server', dest='remote_server', action='store',
                    default="127.0.0.1:31313",
                    help='Set remote server [default=127.0.0.1:31313]')
args = parser.parse_args()

if __name__ == '__main__':
    w = worker.BenchmarkWorker(f"tcp://{args.remote_server}", None, 1, args.cluster_job_id)
    w.run()
