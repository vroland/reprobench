#!/usr/bin/env python
import pandas as pd
import numpy as np
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 2000)

# df = pd.read_csv('output_sat_solvers.csv')
df = pd.read_csv('output_sat_solvers_plingeling_b.csv')
# df = pd.read_csv('output_sat_solvers-2019-01-17.csv')
# print(df)


df['group'] = df['run_id'].apply(lambda row: row.split('/')[1])
df['solver'] = df['run_id'].apply(lambda row: row.split('/')[2])
df['instance'] = df['run_id'].apply(lambda row: '/'.join(row.split('/')[3:]))
df['solver'] = df['solver'].str.replace(r'default\[s=', '').str.replace(r'\]', '')
df['run_id'] = df['run_id'].str.replace(r'output\/glibc\/default\[s=open-wbo_static\]\/maxsat\/', '')
df['run_id'] = df['run_id'].str.replace(r'output\/glibc_thp\/default\[s=open-wbo_static\]\/maxsat\/', '')

# x=df.groupby(['group','solver']) #.agg('wall_time')
# DOUBLE CHECK
glibc = df[((df.solver=='default[s=minisat]') & (df.group=='glibc'))]
glibc_thp = df[((df.solver=='default[s=minisat]') & (df.group=='glibc_thp'))]
print(glibc['instance'].count())
print(glibc_thp['instance'].count())



# print(df)
# exit(1)
x=df.groupby(['group','solver']).size() #.agg(['count']) #.agg('wall_time')
print(x.reset_index(name='counts'))
# print(x.describe())
# exit(1)

df.loc[df.verdict=='TLE', 'wall_time'] = 900
df.loc[df.verdict=='RTE', 'wall_time'] = 900

df.loc[df.verdict=='TLE', 'perf_cache_misses'] = np.nan
df.loc[df.verdict=='TLE', 'perf_tlb_miss'] = np.nan
df.loc[df.verdict=='RTE', 'perf_cache_misses'] = np.nan
df.loc[df.verdict=='RTE', 'perf_tlb_miss'] = np.nan

solver = df #[df.solver=='default[s=minisat]']
print('*'*80)
print('--- NONTHP ---')
glibc=solver[solver.group=='glibc']
# print(glibc)
print('*'*80)
print('--- THP ---')
glibc_thp=solver[solver.group=='glibc_thp']

merged = pd.merge(glibc, glibc_thp, on='instance', how='outer')
print(merged[['hostname_x','hostname_y','run_id_x','run_id_y','wall_time_x','wall_time_y','verdict_x','verdict_y']])
# print(merged.columns)
exit(1)

filtered=merged[((merged.verdict_x=='OK') | (merged.verdict_y=='OK'))]

# filtered = merged[~(((merged.verdict_x == 'OK') & (merged.verdict_y == 'OK'))) & ~((merged.verdict_x == 'TLE') & (merged.verdict_y == 'TLE'))]
# filtered = merged[]

# printme = ['solver_x', 'instance','runsolver_WCTIME_x', 'perf_tlb_miss_x', 'return_code_x', 'verdict_x', 'runsolver_WCTIME_y', 'runsolver_STATUS_y', 'perf_tlb_miss_y', 'verdict_y']
printme = ['solver_x', 'instance','runsolver_WCTIME_x', 'runsolver_WCTIME_y', 'perf_elapsed_x', 'perf_elapsed_y', 'return_code_x', 'return_code_y', 'verdict_x', 'verdict_y', 'perf_tlb_miss_x', 'perf_tlb_miss_y', 'perf_cache_misses_x', 'perf_cache_misses_y']
filtered = filtered[printme].sort_values(by=['instance'])



filtered['perf_tlb_miss_diff'] = filtered['perf_tlb_miss_x']  - filtered['perf_tlb_miss_y']
filtered['perf_cache_misses_diff'] = filtered['perf_cache_misses_x']  - filtered['perf_cache_misses_y']
filtered['perf_elapsed_diff'] = filtered['perf_elapsed_x']  - filtered['perf_elapsed_y']
filtered=filtered[filtered.runsolver_WCTIME_x > 20]
print(filtered)

# exit(1)

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
