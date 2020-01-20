#!/usr/bin/env python
import numpy as np
import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# for filename in ['output_sat_solvers_2020-01-17.csv', 'output_sat_solvers_2020-01-17_plingeling.csv',
#                  'output_sat_solvers-2020-01-17_glucose.csv',
#                  'output_sat_solvers-2020-01-18_lingeling_maple.csv',
#                  'output_maxsat_solvers-2020-01-17_2.csv',
#                  'output_asp_solvers-2020-01-19.csv']:
for filename in ['output_sat_solvers_2020-01-19.csv',
                     'output_maxsat_solvers-2020-01-17_2.csv',
                     'output_asp_solvers-2020-01-19.csv']:
    print('=' * 200)
    print(filename)
    print('=' * 200)
    df = pd.read_csv(filename)

    df['group'] = df['run_id'].apply(lambda row: row.split('/')[1])
    df['solver'] = df['run_id'].apply(lambda row: row.split('/')[2])
    df['instance'] = df['run_id'].apply(lambda row: '/'.join(row.split('/')[3:]))

    # quick overview on solved instances etc...
    z = df.groupby(['group', 'solver', 'verdict']).agg(
        {'wall_time': [np.sum, 'count', np.mean], 'perf_dTLB_load_misses': [np.sum, np.mean],
         'perf_dTLB_loads': [np.sum, np.mean], 'perf_dTLB_store_misses': [np.sum, np.mean],
         'perf_dTLB_stores': [np.sum, np.mean], 'perf_iTLB_load_misses': [np.sum, np.mean],
         'perf_iTLB_loads': [np.sum, np.mean], 'perf_cache_misses': [np.sum, np.mean]})

    z.to_csv(f'1-outputs/{filename}_overview.csv')
    z.to_latex(f'1-outputs/{filename}_overview.tex')

    # solver = df[df.solver=='default[s=minisat]']
    solver = df
    glibc = solver[solver.group == 'glibc']
    glibc_thp = solver[solver.group == 'glibc_thp']

    merged = pd.merge(glibc, glibc_thp, on=['instance', 'solver'], how='outer')
    merged.to_csv(f'1-outputs/{filename}_merged.csv')
    merged.to_latex(f'1-outputs/{filename}_merged.tex')
    # print(merged.columns)

    ok = merged[(merged.verdict_x == 'OK') & (merged.verdict_y == 'OK')]
    ok.to_csv(f'1-outputs/{filename}_merged_both_ok.csv')
    ok.to_latex(f'1-outputs/{filename}_merged_both_ok.tex')
    # print(ok)

    add = merged[~(((merged.verdict_x == 'OK') & (merged.verdict_y == 'OK'))) & ~(
        (merged.verdict_x == 'TLE') & (merged.verdict_y == 'TLE'))]
    printme = ['solver', 'instance', 'runsolver_WCTIME_x', 'return_code_x', 'verdict_x', 'runsolver_WCTIME_y',
               'runsolver_STATUS_y', 'verdict_y']
    add = add[printme].sort_values(by=['instance'])
    add.to_csv(f'1-outputs/{filename}_merged_notok.csv')
    add.to_latex(f'1-outputs/{filename}_merge_notok.tex')

    df1 = df[['instance', 'wall_time', 'perf_dTLB_load_misses', 'perf_cache_misses', 'solver', 'verdict', 'group']]

    x = df1.groupby(['group', 'solver', 'verdict']).agg({'wall_time': np.sum,
                                                         'perf_dTLB_load_misses': np.sum,
                                                         'perf_cache_misses': np.sum})
    x.to_csv(f'1-outputs/{filename}_perf_overview.csv')
    x.to_latex(f'1-outputs/{filename}_perf_overview.tex')

    #
    myf = ok[['group_x', 'solver', 'verdict_x', 'wall_time_x', 'group_y', 'verdict_y', 'wall_time_y']]
    myf.to_csv(f'1-outputs/{filename}_nonthp_thp.csv')
    myf.to_latex(f'1-outputs/{filename}_nonthp_thp.tex')

    # print(ok.columns)
    myff = ok.copy()
    myff = ok.groupby(['solver']).agg({'wall_time_x': [np.sum, 'count'],
                                       'wall_time_y': [np.sum, 'count'],
                                       'perf_dTLB_load_misses_x': np.sum,
                                       'perf_dTLB_load_misses_y': np.sum,
                                       'perf_cache_misses_x': np.sum,
                                       'perf_cache_misses_y': np.sum
                                       }).reset_index()
    myff.to_csv(f'1-outputs/{filename}_nonthp_thp.csv')
    myff.to_latex(f'1-outputs/{filename}_nonthp_thp.tex')

    myff['speedupfact_wall'] = myff[('wall_time_x', 'sum')] / myff[('wall_time_y', 'sum')]
    myff['speedupfact_TLB_load_misses'] = myff[('perf_dTLB_load_misses_x', 'sum')] / \
                                          myff[('perf_dTLB_load_misses_y', 'sum')]
    myff['speedupfact_cache_misses'] = myff[('perf_cache_misses_x', 'sum')] / \
                                       myff[('perf_cache_misses_y', 'sum')]
    myff.to_csv(f'1-outputs/{filename}_summary.csv')
    myff.to_latex(f'1-outputs/{filename}_summary.tex')
