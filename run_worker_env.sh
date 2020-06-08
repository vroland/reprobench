#!/usr/bin/env bash
source /home/jfichte/miniconda3/etc/profile.d/conda.sh
conda activate rb
cd /mnt/vg01/lv01/home/decodyn/reprobench/
python $@
