import pandas as pd
import numpy as np
import os
import glob
import re

os.chdir("/Users/moarplease/Desktop/COCA_results/all_years/")
fnames = glob.glob("*.csv")

df_all = pd.DataFrame()

for filename in fnames:
    df_file = pd.read_csv(filename)
    df_all = df_all.append(df_file)


x = df_all.groupby(['Unnamed: 0'])['pair'].agg('sum')

x.to_csv('all_years.csv', encoding='utf-8')