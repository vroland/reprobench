#!/usr/bin/env python3
import glob
import json
import os

import pandas as pd
from loguru import logger

df = None
folder = f'./output_sparc/**/result.json'

for file in glob.glob(folder, recursive=True):
    run_id = os.path.dirname(file)
    # print(run_id)
    with open(file, "r") as fh:
        d = json.load(fh)

    if df is None:
        df = pd.DataFrame(columns=d.keys())
    df.loc[len(df)] = d


df.to_csv('output_sat_sparc.csv')
