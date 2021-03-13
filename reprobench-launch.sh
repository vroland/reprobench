#!/bin/bash

set -e

source /home/s7300481/.bashrc
conda activate rb
echo "conda active."
module load GCC/9.3.0
module load CUDA/11.0.2-GCC-9.3.0
module load Java/14.0.2
module load util-linux
java -version
(cd experiment/gpusat/tool/wmc/bin/ && echo "1" | ./tw-heuristic)
perf version
/usr/bin/perf stat bash
(python $@)
