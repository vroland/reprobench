#!/usr/bin/env python
import pandas as pd
import numpy as np
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

df = pd.read_csv('output_sat_solvers.csv')
# print(df)


df['group'] = df['run_id'].apply(lambda row: row.split('/')[1])
df['solver'] = df['run_id'].apply(lambda row: row.split('/')[2])
df['instance'] = df['run_id'].apply(lambda row: '/'.join(row.split('/')[3:]))

mergesat = df[df.solver=='default[s=mergesat]']
print('*'*80)
print('--- NONTHP ---')
glibc=mergesat[mergesat.group=='glibc']
# print(glibc)
print('*'*80)
print('--- THP ---')
glibc_thp=mergesat[mergesat.group=='glibc_thp']

merged = pd.merge(glibc, glibc_thp, on='instance', how='outer')
# print(merged)

print(merged[['solver_x', 'instance','runsolver_WCTIME_x', 'perf_tlb_miss_x', 'return_code_x', 'verdict_x', 'runsolver_WCTIME_y', 'runsolver_STATUS_y', 'perf_tlb_miss_y', 'verdict_y']].sort_values(by=['instance']))

# pd.concat([glibc, glibc_thp], axis=1)

exit(1)
df_red=df[['instance','wall_time','perf_elapsed','solver','verdict', 'group']]

df1=df_red

# df1=df_red[df_red.solver=='default[s=plingeling]']
# df1=df_red[df_red.solver=='default[s=minisat]']
# df1=df_red[df_red.solver=='default[s=mergesat]']
# df1=df1[df1.verdict=='OK']
# print(df1)

# x=df1.groupby('group').agg({'wall_time': np.median})
x=df1.groupby(['group','solver']).agg('wall_time')
print(x.describe())
# print(x)
