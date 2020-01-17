#!/usr/bin/env python
import numpy as np
import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# FIXME
# import warnings
# warnings.filterwarnings('ignore')

# df = pd.read_csv('output_asp_solvers_2020_01_14.csv')
# df = pd.read_csv('output_sat_solvers_eperf.csv')
df = pd.read_csv('output_sat_solvers_plingeling_b.csv')
# df = pd.read_csv('output_maxsat_solvers-2020-01-17.csv')
# print(df)


df['group'] = df['run_id'].apply(lambda row: row.split('/')[1])
df['solver'] = df['run_id'].apply(lambda row: row.split('/')[2])
df['instance'] = df['run_id'].apply(lambda row: '/'.join(row.split('/')[3:]))

solver = df[df.solver == 'default[s=minisat]']
print('*' * 80)
print('--- NONTHP ---')
glibc = solver[solver.group == 'glibc']
# print(glibc)
print('*' * 80)
print('--- THP ---')
glibc_thp = solver[solver.group == 'glibc_thp']

merged = pd.merge(glibc, glibc_thp, on='instance', how='outer')
# print(merged)
# filtered=merged[((merged.verdict_x=='OK') & (merged.verdict_y=='OK'))]
filtered = merged[~(((merged.verdict_x == 'OK') & (merged.verdict_y == 'OK'))) & ~(
    (merged.verdict_x == 'TLE') & (merged.verdict_y == 'TLE'))]
# printme = ['solver_x', 'instance','runsolver_WCTIME_x', 'perf_tlb_miss_x', 'return_code_x', 'verdict_x', 'runsolver_WCTIME_y', 'runsolver_STATUS_y', 'perf_tlb_miss_y', 'verdict_y']
printme = ['solver_x', 'instance', 'runsolver_WCTIME_x', 'return_code_x', 'verdict_x', 'runsolver_WCTIME_y',
           'runsolver_STATUS_y', 'verdict_y']
filtered = filtered[printme].sort_values(by=['instance'])
# print(filtered)

df['solver'] = df['solver'].str.replace(r'default\[s=', '').str.replace(r'\]', '')

df_red = df[['instance', 'wall_time', 'solver', 'verdict', 'group', 'perf_dTLB_load_misses', 'perf_dTLB_loads',
             'perf_dTLB_store_misses', 'perf_dTLB_stores', 'perf_iTLB_load_misses', 'perf_iTLB_loads',
             'perf_cache_misses']]
df1 = df_red.copy()

# df1['wall_time'] = np.where((df1.verdict=='TLE'), 900, df1.wall_time)
# df1.where(df1.verdict=='TLE', other=900)
# df1.loc[df1.verdict=='TLE', 'wall_time'] = 900
# df1.loc[df1.wall_time>900, 'wall_time'] = 900
# df1.loc[df1.wall_time>900, 'wall_time'] = 900
df1.loc[df1.verdict == 'TLE', 'wall_time'] = 900
df1.loc[df1.verdict == 'RTE', 'wall_time'] = 900

reset = ['perf_dTLB_load_misses', 'perf_dTLB_loads', 'perf_dTLB_store_misses',
         'perf_dTLB_stores', 'perf_iTLB_load_misses', 'perf_iTLB_loads', 'perf_cache_misses']
for i in reset:
    df1.loc[df1.verdict == 'TLE', i] = np.nan
    df1.loc[df1.verdict == 'RTE', i] = np.nan

# print(df1[df1.verdict=='TLE'])
# exit(1)

# df1=df_red[df_red.solver=='default[s=plingeling]']
# df1=df_red[df_red.solver=='default[s=minisat]']
# df1=df_red[df_red.solver=='default[s=mergesat]']
# df1=df1[df1.verdict=='OK']
# print(df1)

# x=df1.groupby('group').agg({'wall_time': np.median})
# x=df1.groupby(['group','solver']).agg({'wall_time': [np.sum, np.mean], 'perf_tlb_miss': [np.sum, np.mean], 'perf_cache_misses': [np.sum, np.mean]})
z = df1.groupby(['group', 'solver']).agg(
    {'wall_time': [np.sum, 'count', np.mean], 'perf_dTLB_load_misses': [np.sum, np.mean],
     'perf_dTLB_loads': [np.sum, np.mean], 'perf_dTLB_store_misses': [np.sum, np.mean],
     'perf_dTLB_stores': [np.sum, np.mean], 'perf_iTLB_load_misses': [np.sum, np.mean],
     'perf_iTLB_loads': [np.sum, np.mean], 'perf_cache_misses': [np.sum, np.mean]})
print(z)
# x.drop(('count'), axis=1, level=1, inplace=True)

for column in ['wall_time', 'perf_dTLB_load_misses', 'perf_dTLB_loads', 'perf_dTLB_store_misses',
               'perf_dTLB_stores', 'perf_iTLB_load_misses', 'perf_iTLB_loads', 'perf_cache_misses']:
    print('=' * 120)
    print(column)
    x = df1.groupby(['group', 'solver']).agg({column: [np.sum, np.mean, np.median]})

    xd = x.reset_index()
    glibc = xd[xd.group == 'glibc']
    glibc_thp = xd[xd.group == 'glibc_thp']

    xd_m = pd.merge(glibc, glibc_thp, on=('solver'), how='outer')
    # xd_m = xd_m.drop(columns=[('wall_time_x', 'count'), ('wall_time_y', 'count')])
    # xd_m = xd_m.drop(columns=[('group_x', level=0), ('group_y', level=0)])
    # TODO: wired python/pandas error HERE
    # xd_m=xd_m.drop('group_x', axis=1, level=0)
    # xd_m=xd_m.drop('group_y', axis=1, level=0)
    # print(xd_m)
    # print(xd_m.columns)
    # xd_m.reset_index()
    # xd_m=xd_m.drop('group_y', axis=1, level=0)

    names = {'%s_x' % column: 'Original', '%s_y' % column: '+THP'}
    xd_m.rename(names, axis='columns', inplace=True)
    print(xd_m)

    xd_m['Speedup'] = (xd_m[('Original', 'sum')] / xd_m[('+THP', 'sum')])
    xd_m['Saved'] = (xd_m[('Original', 'sum')] - xd_m[('+THP', 'sum')])

    # in hours
    fields = [('Original', 'sum'), ('Original', 'mean'), ('+THP', 'sum'), ('+THP', 'mean'), 'Saved']
    for f in fields:
        xd_m[f] = xd_m[f] / 3600
    # rounding
    for f in fields:
        xd_m[f] = xd_m[f].round(1)
    xd_m['Speedup'] = xd_m['Speedup'].round(2)
    print('*' * 100)
    print(xd_m)
    print('*' * 100)

    print(xd_m.to_latex())

    # print(x.describe())
    # print(x)
