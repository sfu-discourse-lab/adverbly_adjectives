import pandas as pd
import numpy as np
import os
import glob
import re

# set these for each category
os.chdir("/Users/moarplease/Desktop/COCA/POS/wlp_magazine_qwi/")
category = 'mag'

# get all the filenames that end in 'txt'
fnames = glob.glob("*.txt")

df_all = pd.DataFrame()
df_1990 = pd.DataFrame()
df_1995 = pd.DataFrame()
df_2000 = pd.DataFrame()
df_2005 = pd.DataFrame()
df_2010 = pd.DataFrame()
#df_2015 = pd.DataFrame()


for filename in fnames:
    year = re.compile(r'\d+').findall(filename)

    # for the old POS files
    if not filename[:4].isdigit():
        df_file = pd.read_csv(filename, encoding='latin1', skiprows=[0], sep='\t', error_bad_lines=False, quoting=3,
                              lineterminator='\r', header=None)
        df_file.columns = ['word', 'lemma', 'pos']
        # add a column for the next word and POS
        df_file["nextword"] = df_file["word"].shift(1)
        df_file["nextpos"] = df_file['pos'].shift(1)

        # search for POS adv (rr) ending in -ly followed by POS adj (jj)
        # if the rr/jj is the first tag in an ambiguity tag pair
        # filter for slashes or hyphens
        df_file = df_file[(df_file['pos'].str[:2] == 'rr') & (df_file['word'].str[-2:] == 'ly') & (~df_file['word'].str.contains("-|/",  na=False))
                      & (df_file['nextpos'].str[:2] == 'jj') & (~df_file['nextword'].str.contains("-|/",  na=False))]
        df_file = df_file[['word', 'pos', 'nextword', 'nextpos']]

        # trim a bit
        df_file['word'] = df_file['word'].str[1:]
        df_file['nextword'] = df_file['nextword'].str[1:]

        # lowercase
        df_file['word'] = df_file['word'].str.lower()
        df_file['nextword'] = df_file['nextword'].str.lower()

        # add a column for the adv adj pair
        df_file['pair'] = df_file['word'] + " " + df_file['nextword']
        df_file = df_file.drop(columns=['word', 'pos', 'nextword', 'nextpos'], axis=1)
        # get the counts of each pair
        df_file = df_file.apply(pd.value_counts).fillna(0)

    # for the newer POS files (after 2012+)
    if filename[:4].isdigit():

        # newer POS files have different columns
        df_file = pd.read_csv(filename, encoding='latin1', skiprows=[0], sep='\t', error_bad_lines=False, quoting=3,
                              lineterminator='\r', header=None, index_col=1)
        df_file.columns = ['textid', 'word', 'lemma', 'pos']
        df_file["nextword"] = df_file["word"].shift(-1)
        df_file["nextpos"] = df_file['pos'].shift(-1)

        df_file = df_file[(df_file['pos'].str[:2] == 'rr') & (df_file['word'].str[-2:] == 'ly') & (~df_file['word'].str.contains("-|/", na=False))
                          & (df_file['nextpos'].str[:2] == 'jj') & (~df_file['nextword'].str.contains("-|/", na=False))]
        df_file = df_file[['word', 'pos', 'nextword', 'nextpos']]

        df_file = df_file.iloc[1:]

        df_file['word'] = df_file['word'].str.lower()
        df_file['nextword'] = df_file['nextword'].str.lower()

        df_file['pair'] = df_file['word'] + " " + df_file['nextword']
        df_file = df_file.drop(columns=['word', 'pos', 'nextword', 'nextpos'], axis=1)
        df_file = df_file.apply(pd.value_counts).fillna(0)

    # append each file to a df for 5 year intervals
    if int(year[0]) < 1995:
        df_1990 = df_1990.append(df_file)
    elif int(year[0]) < 2000:
        df_1995 = df_1995.append(df_file)
    elif int(year[0]) < 2005:
        df_2000 = df_2000.append(df_file)
    elif int(year[0]) < 2010:
        df_2005 = df_2005.append(df_file)
    elif int(year[0]) < 2016:
        df_2010 = df_2010.append(df_file)

    # append to df containing all the years
    df_all = df_all.append(df_file)

# write everything to csv
df_1990.to_csv(category + '1990.csv', encoding='utf-8')
df_1995.to_csv(category + '1995.csv', encoding='utf-8')
df_2000.to_csv(category + '2000.csv', encoding='utf-8')
df_2005.to_csv(category + '2005.csv', encoding='utf-8')
df_2010.to_csv(category + '2010.csv', encoding='utf-8')

df_all.to_csv(category + 'all_years.csv', encoding='utf-8')

