#!/usr/bin/env python3
import re

import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
# pd.options.mode.chained_assignment = 'warn'

config_re = re.compile(r"default\[s=(?P<solver>([\w\.-]+))\]")

for filename in ['output_sat_sparc.csv']:
    print('=' * 200)
    print(filename)
    print('=' * 200)
    df = pd.read_csv(filename)

    df['instance'] = df['run_id'].apply(lambda row: '/'.join(row.split('/')[3:-1]))
    df['run'] = df['run_id'].apply(lambda row: int(row.split('/')[-1]))
    df['solver'] = df['run_id'].apply(lambda row: re.findall(config_re, row.split('/')[3])[0][0])

    print(df)
    group = df.groupby(['run', 'verdict']).agg({'run_id': 'count'})
    print(group)


