#!/usr/bin/env python
import pandas as pd
import numpy as np
df = pd.read_csv('output_sat.csv')
# print(df)

df['group'] = df['run_id'].apply(lambda row: row.split('/')[1])
df['solver'] = df['run_id'].apply(lambda row: row.split('/')[2])
df['instance'] = df['run_id'].apply(lambda row: '/'.join(row.split('/')[3:]))

df_red=df[['instance','wall_time','perf_elapsed','solver','verdict', 'group']]

df1=df_red[df_red.solver=='default[s=plingeling]']
df1=df_red[df_red.solver=='default[s=minisat]']
# df1=df_red[df_red.solver=='default[s=mergesat]']
# df1=df1[df1.verdict=='OK']
# print(df1)

# x=df1.groupby('group').agg({'wall_time': np.median})
x=df1.groupby('group').agg('wall_time')
print(x.describe())
# print(x)
