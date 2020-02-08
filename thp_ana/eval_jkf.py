#!/usr/bin/env python
import numpy as np
from pandas.plotting import scatter_matrix
import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
# pd.options.mode.chained_assignment = 'warn'

import matplotlib as mpl

mpl.use('Agg')
import matplotlib.pyplot as plt

# for filename in ['output_sat_solvers_2020-01-17.csv', 'output_sat_solvers_2020-01-17_plingeling.csv',
#                  'output_sat_solvers-2020-01-17_glucose.csv',
#                  'output_sat_solvers-2020-01-18_lingeling_maple.csv',
#                  'output_maxsat_solvers-2020-01-17_2.csv',
#                  'output_asp_solvers-2020-01-19.csv']:
# for filename in ['output_sat_solvers_2020-01-19.csv',
#                      'output_maxsat_solvers-2020-01-17_2.csv',
#                      'output_asp_solvers-2020-01-19.csv']:
#
#SUBMISSION VERSION!!
#for filename in ['output_sat_solvers_2020-01-20.csv']:
#
#output_THP.csv
for filename in ['output_THP_sat_t0_1-3.csv']:
    print('=' * 200)
    print(filename)
    print('=' * 200)
    df = pd.read_csv(filename)

    df['instance'] = df['run_id'].apply(lambda row: '/'.join(row.split('/')[3:-1]))
    df['run'] = df['run_id'].apply(lambda row: row.split('/')[-1])
    df['group'] = df['run_id'].apply(lambda row: row.split('/')[1])
    df['solver'] = df['run_id'].apply(lambda row: row.split('/')[2])
    df['instance'] = df['run_id'].apply(lambda row: '/'.join(row.split('/')[3:-1]))
    df['hostname'] = df['hostname'].apply(lambda row: row.split('.')[0])

    # quick overview on solved instances etc...
    z = df.groupby(['group', 'run', 'solver', 'verdict']).agg(
        {'wall_time': [np.sum, 'count', np.mean], 'perf_dTLB_load_misses': [np.sum, np.mean],
         'perf_dTLB_loads': [np.sum, np.mean], 'perf_dTLB_store_misses': [np.sum, np.mean],
         'perf_dTLB_stores': [np.sum, np.mean], 'perf_iTLB_load_misses': [np.sum, np.mean],
         'perf_iTLB_loads': [np.sum, np.mean], 'perf_cache_misses': [np.sum, np.mean]})

    z.to_csv(f'1-outputs/{filename}_overview.csv')
    z.to_latex(f'1-outputs/{filename}_overview.tex')

    #--------------------------------------------------------------------------------------------
    # memory footprint solved instances
    #--------------------------------------------------------------------------------------------
    mem = df.copy()
    mem = mem[mem.verdict == 'OK']
    mem['solver'] = mem['solver'].str.replace(r'default\[s=', '').str.replace(r'\]', '')
    mem['group'] = mem['group'].str.replace(r'_', '')
    mem['run'] = mem['run_id'].apply(lambda row: row.split('/')[-1])
    mem['solver'] = mem['solver'].str.replace(r'default\[s=', '').str.replace(r'\]', '')
    mem['solver'] = mem['solver'].str.replace('MapleLCMDiscChronoBT-DL-v3', 'maplesat')
    mem['solver'] = mem['solver'].str.replace('glucose-4.2.1', 'glucose')
    mem['solver_t'] = mem["solver"].map(str) + '-' + mem["group"]\

    mem['runsolver_MAXVM'] = mem['runsolver_MAXVM'] / 1024
    mem = mem[['solver_t', 'solver','group', 'run', 'instance', 'runsolver_MAXVM', 'wall_time', 'perf_dTLB_load_misses']]

    # print(mem)
    print(mem['runsolver_MAXVM'].quantile([0.05,0.1,0.25,0.5,0.75,1]))

    print('*'*80)
    print('Below 1M')
    print('*'*80)
    below1M = mem[mem.runsolver_MAXVM <= 1].groupby(['solver', 'group', 'run']).agg({'runsolver_MAXVM': 'count'})
    print(below1M)
    print('*'*80)
    print('Below 10M')
    print('*'*80)
    below10M = mem[(mem.runsolver_MAXVM > 1) & (mem.runsolver_MAXVM <= 10)].groupby(['solver', 'group', 'run']).agg({'runsolver_MAXVM': 'count'})
    print(below10M)
    print('*'*80)
    print('Below 100M')
    print('*'*80)
    below100M = mem[(mem.runsolver_MAXVM > 10) & (mem.runsolver_MAXVM <= 400)].groupby(['solver', 'group', 'run']).agg({'runsolver_MAXVM': 'count'})
    print(below100M)

    mmem = mem.groupby(['solver', 'group', 'run']).agg({'runsolver_MAXVM': ['count', np.mean, np.median]})
    print(mmem.reset_index())

    mconfigs = mem['solver_t'].unique()
    NUM_COLORS = len(mconfigs) + 1
    plt.rc('font', family='serif')
    # plt.rc('text', usetex=True)
    plt.rcParams['text.usetex'] = True
    plt.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}\def\hy{\hbox{-}\nobreak\hskip0pt}']

    fig = plt.figure()
    ax = fig.add_subplot(111)

    lfont = lambda x: '$\mathtt{%s}$' % x.replace('-', '\hy')
    color_m = {'lingeling-glibcthp': ('lingeling(thp)', '#a6cee3', '-'),
               'lingeling-glibc': ('lingeling', '#1f78b4', '-'),
               'glucose-glibc': ('glucose', '#33a02c', '-'),
               'glucose-glibcthp': ('glucose(thp)', '#b2df8a', '-'),
               'minisat,t=0-sat': ('minisat', '#e31a1c', '-'),
               'minisat,t=1-sat': ('minisat(thp)', '#fb9a99', '-'),
               'maplesat-glibc': ('maplesat', '#ff7f00', '-'),
               'maplesat-glibcthp': ('maplesat(thp)', '#fdbf6f', '-'),
               'mergesat-glibc': ('mergesat', '#6a3d9a', '-'),
               'mergesat-glibcthp': ('mergesat(thp)', '#cab2d6', '-'),
               'plingeling-glibc': ('plingeling', '#b15928', '-'),
               'plingeling-glibcthp': ('plingeling(thp)', '#ffff99', '-'),
               }
    skip = ['maplesat-glibc', 'maplesat-glibcthp',
            'lingeling-glibc', 'lingeling-glibcthp',
            'minisat-glibc', 'minisat-glibcthp',
            'mergesat-glibc', 'mergesat-glibcthp',
            'plingeling-glibc', 'plingeling-glibcthp']

    for key in mconfigs:
        # if key in skip:
        #     continue
        solver_df = mem[(mem['solver_t'] == key)]
        pd.options.mode.chained_assignment = None
        solver_df.sort_values(by=['runsolver_MAXVM'], inplace=True)
        pd.options.mode.chained_assignment = 'warn'
        solver_df.reset_index(inplace=True)
        ts = pd.Series(solver_df['runsolver_MAXVM'])
        # label = lfont(mapping[key][1]) if mapping.has_key(key) else key
        # , ylim = [10, 1000]
        #
        ax = ts.plot(markeredgecolor='none', label=color_m[key][0],
                    color=color_m[key][1], linestyle=color_m[key][2])
        # ax = ts.plot(markeredgecolor='none', label=label, color=mapping[key][2], linestyle=mapping[key][3])

    fig.subplots_adjust(bottom=0.3, left=0.1)
    handles, labels = ax.get_legend_handles_labels()
    labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
    # print labels
    # ax.set_yscale('log')
    ax.legend(handles, labels, loc='best', prop={'size': 6}, frameon=False, mode='expand')
    # ax.tick_params(axis='x', which='minor', bottom='off')
    plt.minorticks_on()
    plt.savefig('%s-%s.pdf' % (filename, 'runsolver_MAXVM'), bbox_inches="tight")  #
    #--------------------------------------------------------------------------------------------
    # exit(1)

    # solver = df[df.solver=='default[s=minisat]']
    solver = df
    glibc = solver[solver.group == 'glibc']
    glibc_thp = solver[solver.group == 'glibc_thp']

    merged = pd.merge(glibc, glibc_thp, on=['instance', 'solver','run'], how='outer')
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

    df1 = df[['instance', 'wall_time', 'perf_dTLB_load_misses', 'perf_cache_misses', 'solver', 'verdict', 'group', 'run', 'hostname']]

    x = df1.groupby(['group', 'run', 'solver', 'verdict','hostname']).agg({'wall_time': np.sum,
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
    myff = ok.groupby(['solver', 'run']).agg({'wall_time_x': [np.sum, 'count'],
                                       'wall_time_y': [np.sum, 'count'],
                                       'runsolver_MAXVM_x': np.mean,
                                       'runsolver_MAXVM_y': np.mean,
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

    print(myff.columns)
    myff[('wall_time_x', 'sum')] = (myff[('wall_time_x', 'sum')] / 3600).round(2)
    myff[('wall_time_y', 'sum')] = (myff[('wall_time_y', 'sum')] / 3600).round(2)

    mygf = myff.copy()
    mygf['solver'] = mygf['solver'].replace(r'default\[s=', '').replace(r'\]', '')
    mygf['count'] = mygf[('wall_time_x', 'count')]
    mygf['t[h]'] = mygf[('wall_time_x', 'sum')]
    mygf['t_thp[h]'] = mygf[('wall_time_y', 'sum')]
    mygf['m[MB]'] = (mygf[('runsolver_MAXVM_x', 'mean')] / 1024).round(1)
    mygf['m_thp[MB]'] = (mygf[('runsolver_MAXVM_y', 'mean')] / 1024).round(1)
    mygf['TLB'] = mygf[('perf_dTLB_load_misses_x', 'sum')]
    mygf['TLB_thp'] = mygf[('perf_dTLB_load_misses_y', 'sum')]

    # mygf['TLB'] = mygf['TLB'].apply(lambda x: '{:.2E}'.format(x))
    # mygf['TLB_thp'] = mygf['TLB_thp'].apply(lambda x: '{:.2E}'.format(x))
    mygf['TLB'] = (mygf['TLB']  / 1000000).round(1).apply(lambda x: "{:,}".format(x))
    mygf['TLB_thp'] = (mygf['TLB_thp']/ 1000000).round(1).apply(lambda x: "{:,}".format(x))

    # print(mygf)
    # exit(1)
    mygf['s[t]'] = mygf['speedupfact_wall'].round(2)
    mygf['s[tlb]'] = mygf['speedupfact_TLB_load_misses'].round(2)
    mygf['r[tlb]'] = ((myff[('perf_dTLB_load_misses_y', 'sum')] /
                                          myff[('perf_dTLB_load_misses_x', 'sum')]) * 100).round(2)

    output = mygf[['solver', 'count', 't[h]', 't_thp[h]', 's[t]', 'm[MB]', 'm_thp[MB]', 'TLB', 'TLB_thp', 's[tlb]', 'r[tlb]']]

    output['solver'] = output['solver'].replace('MapleLCMDiscChronoBT-DL-v3', 'maplesat')
    output['solver'] = output['solver'].replace('glucose-4.2.1', 'glucose')

    output = output.sort_values(by=['solver'])

    print(output)
    output.to_latex(f'1-outputs/{filename}_zz_paper.tex')

    #CACTUS
    # cactus = df[(df.verdict == 'OK')]
    cactus = df.copy()

    cactus['group'] = cactus['group'].str.replace(r'_', '')
    cactus['solver'] = cactus['solver'].str.replace(r'default\[s=', '').str.replace(r'\]', '')
    cactus['solver'] = cactus['solver'].str.replace('MapleLCMDiscChronoBT-DL-v3', 'maplesat')
    cactus['solver'] = cactus['solver'].str.replace('glucose-4.2.1', 'glucose')

    cactus['solver_t'] = cactus["solver"].map(str) + '-' + cactus["group"]\
        #.replace('glibc_','').replace('glibc','')
    # print(cactus[['solver','group','instance','wall_time']])

    cactus.sort_values(by=['wall_time'], inplace=True)
    print(cactus[['solver_t','run','instance','wall_time']])

    configs = cactus['solver_t'].unique()
    NUM_COLORS = len(configs) + 1
    plt.rc('font', family='serif')
    # plt.rc('text', usetex=True)
    plt.rcParams['text.usetex'] = True
    plt.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}\def\hy{\hbox{-}\nobreak\hskip0pt}']


    lfont = lambda x: '$\mathtt{%s}$' % x.replace('-', '\hy')
    color_m = {'lingeling-glibcthp': ('lingeling(thp)', '#a6cee3', '-'),
               'lingeling-glibc': ('lingeling', '#1f78b4', '-'),
               'glucose-glibc': ('glucose', '#33a02c', '-'),
               'glucose-glibcthp': ('glucose(thp)', '#b2df8a', '-'),
               'minisat,t=0-sat': ('minisat', '#e31a1c', '-'),
               'minisat,t=1-sat': ('minisat(thp)', '#fb9a99', '-'),
               'maplesat-glibc': ('maplesat', '#ff7f00', '-'),
               'maplesat-glibcthp': ('maplesat(thp)', '#fdbf6f', '-'),
               'mergesat-glibc': ('mergesat', '#6a3d9a', '-'),
               'mergesat-glibcthp': ('mergesat(thp)', '#cab2d6', '-'),
               'plingeling-glibc': ('plingeling', '#b15928', '-'),
               'plingeling-glibcthp': ('plingeling(thp)', '#ffff99', '-'),
               }
    skip = ['maplesat-glibc', 'maplesat-glibcthp',
            'lingeling-glibc', 'lingeling-glibcthp',
            'minisat-glibc', 'minisat-glibcthp',
            'mergesat-glibc', 'mergesat-glibcthp',
            'plingeling-glibc', 'plingeling-glibcthp']

    fig = plt.figure()
    ax = fig.add_subplot(111)

    runs = cactus['run'].unique()
    for key in configs:
        collect = None
        for run in runs:
            # if key in skip:
            #     continue
            solver_df = cactus[(cactus['solver_t'] == key) & (cactus['run'] == run)]
            pd.options.mode.chained_assignment = None
            solver_df.sort_values(by=['wall_time'], inplace=True)
            pd.options.mode.chained_assignment = 'warn'
            solver_df.reset_index(inplace=True)
            ts = pd.Series(solver_df['wall_time'])
            # label = lfont(mapping[key][1]) if mapping.has_key(key) else key
            # , ylim = [10, 1000]
            #
            ax = ts.plot(xlim=125, markeredgecolor='none', label=(color_m[key][0], run),
                        color=color_m[key][1], linestyle=color_m[key][2])
            # ax = ts.plot(markeredgecolor='none', label=label, color=mapping[key][2], linestyle=mapping[key][3])
            if collect is None:
                collect = solver_df[['instance', 'wall_time']]
                # collect['wall_time']=pd.to_numeric(collect['wall_time'], errors='coerce')
            else:
                collect = pd.merge(collect, solver_df[['instance', 'wall_time']], on=['instance'], how='outer')
                run1 = int(run)+1
                collect.rename({'wall_time': f'wall{run}', 'wall_time_y': f'wall{run}', 'wall_time_x': f'wall{run1}'}, inplace=True, axis='columns')

        cols = list(map(lambda x: f'wall{x}', runs))
        print(collect.columns)
        collect['min']=collect[cols].min(axis=1)
        collect['max']=collect[cols].max(axis=1)
        collect['diff']=collect['max']-collect['min']
        # pd.set_option('precision', 2)
        collect.to_csv(f'1-outputs/{filename}_{color_m[key][0]}_runs_overview.csv', float_format="%.1f")

        fig_scatter = plt.figure()
        ax_sc = fig_scatter.add_subplot(111)
        collect.drop(['instance', 'min', 'max', 'diff'], axis=1, inplace=True)
        scatter_matrix(collect, ax=ax_sc, grid=True, alpha=0.6, marker='.', figsize=(30,30), diagonal='hist')
        fig_scatter.savefig(f'1-outputs/{filename}-{color_m[key][0]}_scatter_wall_time.pdf', bbox_inches="tight")  # ,

    fig.subplots_adjust(bottom=0.3, left=0.1)
    handles, labels = ax.get_legend_handles_labels()
    labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
    # print labels
    # ax.set_yscale('log')
    ax.legend(handles, labels, loc='best', prop={'size': 6}, frameon=False, mode='expand')
    fig.savefig('1-outputs/%s-%s.pdf' % (filename, 'wall_time'), bbox_inches="tight")  # ,

    # plot.reset_index(inplace=True)

