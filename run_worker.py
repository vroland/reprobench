#!/home/decodyn/reprobench/run_worker_env.sh
#/home/jfichte/anaconda3/condabin/
import argparse

import yaml

import reprobench.core.worker as worker

parser = argparse.ArgumentParser(description='%(prog)s -r remoteid:port -i cluster_job_id')
parser.add_argument('-i', '--cluster_job_id', dest='cluster_job_id', action='store',
                    default=-1, help='Set cluster_job_id [default=-1]')
parser.add_argument('-r', '--remote-server', dest='remote_server', action='store',
                    default="127.0.0.1:31313",
                    help='Set remote server [default=127.0.0.1:31313]')
args = parser.parse_args()

mconfig = None
with open('./benchmark_system_config.yml') as config_f:
    try:
        mconfig = yaml.safe_load(config_f)
    except yaml.YAMLError as exc:
        print(exc)
        exit(1)

if __name__ == '__main__':
    w = worker.BenchmarkWorker(server_address=f"tcp://{args.remote_server}", tunneling=None, multicore=mconfig['multicore'],
                               cluster_job_id=args.cluster_job_id)
    w.run()
