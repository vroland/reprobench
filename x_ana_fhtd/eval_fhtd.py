#!/usr/bin/env python
import os

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

for filename in ['output_FHTD_2020-03-28.csv']:
    print('=' * 200)
    print(filename)
    print('=' * 200)
    df = pd.read_csv(filename)

    df['instance'] = df['run_id'].apply(lambda row: '/'.join(row.split('/')[3:-1]))
    df['run'] = df['run_id'].apply(lambda row: int(row.split('/')[-1]))
    df['group'] = df['run_id'].apply(lambda row: row.split('/')[2].split('+')[1]) #[-4:-1])

    df['solver'] = df['run_id'].apply(lambda row: row.split('/')[1])
    df['solver_t'] = df["solver"].map(str) + ',' + df["group"]
    df['instance'] = df['run_id'].apply(lambda row: '/'.join(row.split('/')[3:-1]))
    df['hostname'] = df['hostname'].apply(lambda row: row.split('.')[0])

    # Restricting run to 0 only
    df = df[df.run == 0]

    # quick overview on solved instances etc...
    z = df.groupby(['group', 'run', 'solver', 'verdict']).agg(
        {'wall_time': [np.sum, 'count', np.mean], 'perf_dTLB_load_misses': [np.sum, np.mean],
         'perf_dTLB_loads': [np.sum, np.mean], 'perf_dTLB_store_misses': [np.sum, np.mean],
         'perf_dTLB_stores': [np.sum, np.mean], 'perf_iTLB_load_misses': [np.sum, np.mean],
         'perf_iTLB_loads': [np.sum, np.mean], 'perf_cache_misses': [np.sum, np.mean]})

    if not os.path.exists('1-outputs/'):
        os.makedirs("1-outputs/")
    z.to_csv(f'1-outputs/{filename}_overview.csv')
    z.to_latex(f'1-outputs/{filename}_overview.tex')

    # --------------------------------------------------------------------------------------------
    # memory footprint solved instances
    # --------------------------------------------------------------------------------------------
    mem = df.copy()
    mem = mem[mem.verdict == 'OK']
    mem['solver'] = mem['solver'].str.replace(r'default\[s=', '').str.replace(r'\]', '')

    mem['runsolver_MAXVM'] = mem['runsolver_MAXVM'] / 1024
    mem = mem[['solver', 'group', 'solver_t', 'run', 'instance', 'runsolver_MAXVM', 'wall_time', 'perf_dTLB_load_misses']]

    mem.to_csv(f'1-outputs/{filename}_mem.csv')
    mem.to_latex(f'1-outputs/{filename}_mem.tex')

    # print(mem)
    print(mem['runsolver_MAXVM'].quantile([0.05, 0.1, 0.25, 0.5, 0.75, 1]))
    mmem = mem.groupby(['solver', 'group', 'run']).agg({'runsolver_MAXVM': ['count', np.mean, np.median]})
    print(mmem.reset_index())
    mmem.to_csv(f'1-outputs/{filename}_mmem.csv')
    mmem.to_latex(f'1-outputs/{filename}_mmem.tex')

    mconfigs = mem['solver_t'].unique()
    NUM_COLORS = len(mconfigs) + 1
    plt.rc('font', family='serif')
    # plt.rc('text', usetex=True)
    plt.rcParams['text.usetex'] = True
    plt.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}\def\hy{\hbox{-}\nobreak\hskip0pt}']

    fig = plt.figure()
    ax = fig.add_subplot(111)

    lfont = lambda x: '$\mathtt{%s}$' % x.replace('-', '\hy')
    color_m = {'fhtd,z3-4.8.7-x64-ubuntu-16.04': ('fhtd(z3)', '#a6cee3', '-'),
               'fhtd,optimathsat': ('fhtd(optimathsat)', '#fb9a99', '-'),
               }
    skip = []

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
    plt.savefig(f'1-outputs/{filename}-runsolver_MAXVM.pdf', bbox_inches="tight")  #
    # --------------------------------------------------------------------------------------------

    # CACTUS
    # cactus = df[(df.verdict == 'OK')]
    cactus = df.copy()

    cactus['group'] = cactus['group'].str.replace(r'_', '')
    cactus['solver'] = cactus['solver'].str.replace(r'default\[s=', '').str.replace(r'\]', '')
    cactus['solver'] = cactus['solver'].str.replace('MapleLCMDiscChronoBT-DL-v3', 'maplesat')
    cactus['solver'] = cactus['solver'].str.replace('glucose-4.2.1', 'glucose')

    cactus['solver_t'] = cactus["solver"].map(str) + ',' + cactus["group"] \
        # .replace('glibc_','').replace('glibc','')
    # print(cactus[['solver','group','instance','wall_time']])

    cactus.sort_values(by=['wall_time'], inplace=True)
    print(cactus[['solver_t', 'run', 'instance', 'wall_time']])

    configs = cactus['solver_t'].unique()
    NUM_COLORS = len(configs) + 1
    plt.rc('font', family='serif')
    # plt.rc('text', usetex=True)
    plt.rcParams['text.usetex'] = True
    plt.rcParams['text.latex.preamble'] = [r'\usepackage{amsmath}\def\hy{\hbox{-}\nobreak\hskip0pt}']

    lfont = lambda x: '$\mathtt{%s}$' % x.replace('-', '\hy')

    fig = plt.figure()
    ax = fig.add_subplot(111)


    #OUTPUT THE RUNS
    runs = cactus['run'].unique()
    if len(runs) > 1:
        last_run = 0
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
                    last_run = int(run) - 1
                    collect = pd.merge(collect, solver_df[['instance', 'wall_time']], on=['instance'], how='outer',
                                       suffixes=(f'_{last_run}', f'_{run}'))

            collect.rename({'wall_time': f'wall_time_{run}'}, inplace=True, axis='columns')
            collect.rename({f'wall_time_{run}': f'wall{run}' for run in runs}, inplace=True, axis='columns')

            cols = list(map(lambda x: f'wall{x}', runs))
            print(collect.columns)
            collect['min'] = collect[cols].min(axis=1)
            collect['max'] = collect[cols].max(axis=1)
            collect['diff'] = collect['max'] - collect['min']
            # pd.set_option('precision', 2)
            collect.to_csv(f'1-outputs/{filename}_{color_m[key][0]}_runs_overview.csv', float_format="%.1f")

            fig_scatter = plt.figure()
            ax_sc = fig_scatter.add_subplot(111)
            collect.drop(['instance', 'min', 'max', 'diff'], axis=1, inplace=True)
            scatter_matrix(collect, ax=ax_sc, grid=True, alpha=0.6, marker='.', figsize=(30, 30), diagonal='hist')
            fig_scatter.savefig(f'1-outputs/{filename}-{color_m[key][0]}_scatter_wall_time.pdf',
                                bbox_inches="tight")  # ,

    else:
        for key in configs:
            solver_df = cactus[(cactus['solver_t'] == key)]
            pd.options.mode.chained_assignment = None
            solver_df.sort_values(by=['wall_time'], inplace=True)
            pd.options.mode.chained_assignment = 'warn'
            solver_df.reset_index(inplace=True)
            ts = pd.Series(solver_df['wall_time'])
            # label = lfont(mapping[key][1]) if mapping.has_key(key) else key
            # , ylim = [10, 1000]
            #
            ax = ts.plot(xlim=125, markeredgecolor='none', label=color_m[key][0],
                         color=color_m[key][1], linestyle=color_m[key][2])
            # ax = ts.plot(markeredgecolor='none', label=label, color=mapping[key][2], linestyle=mapping[key][3])


    fig.subplots_adjust(bottom=0.3, left=0.1)
    handles, labels = ax.get_legend_handles_labels()
    labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
    # print labels
    # ax.set_yscale('log')
    ax.legend(handles, labels, loc='best', prop={'size': 6}, frameon=False, mode='expand')
    fig.savefig(f'1-outputs/{filename}-wall_time.pdf', bbox_inches="tight")  # ,

    # plot.reset_index(inplace=True)
