import pandas as pd
import os
import glob
import re

# set these for each category
os.chdir("/Users/moarplease/Desktop/COCA/POS/wlp_newspaper_lsp/")
category = 'news'

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
    # btw the year 2012 has 2 files (1 old, 1 new)
    if not filename[:4].isdigit():
        df_file = pd.read_csv(filename, encoding='latin1', skiprows=[0], sep='\t', error_bad_lines=False, quoting=3,
                              lineterminator='\r', header=None, index_col=None)
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


    # for the newer POS files (after 2012)
    if filename[:4].isdigit():

        # newer POS files have different columns
        df_file = pd.read_csv(filename, encoding='latin1', skiprows=[0], sep='\t', error_bad_lines=False, quoting=3,
                              lineterminator='\r', header=None, index_col=None)
        df_file.columns = ['index','textid', 'word', 'lemma', 'pos']
        df_file["nextword"] = df_file["word"].shift(-1)
        df_file["nextpos"] = df_file['pos'].shift(-1)

        df_file = df_file[(df_file['pos'].str[:2] == 'rr') & (df_file['word'].str[-2:] == 'ly') & (~df_file['word'].str.contains("-|/", na=False))
                          & (df_file['nextpos'].str[:2] == 'jj') & (~df_file['nextword'].str.contains("-|/", na=False))]
        df_file = df_file[['word', 'pos', 'nextword', 'nextpos']]

        # eliminate first row
        df_file = df_file.iloc[1:]

        df_file['word'] = df_file['word'].str.lower()
        df_file['nextword'] = df_file['nextword'].str.lower()

        df_file['pair'] = df_file['word'] + " " + df_file['nextword']
        df_file = df_file.drop(columns=['word', 'pos', 'nextword', 'nextpos'], axis=1)

    # get the count for each pair
    df_file['count'] = df_file.groupby('pair', as_index=False)['pair'].transform(lambda s: s.count())

    # get rid of duplicates
    df_file = df_file.drop_duplicates(subset=['pair'])
    df_file = df_file.set_index('pair')

    # append each file to a df for 5 year intervals
    if int(year[0]) < 1995:
        df_1990 = df_1990.add(df_file, fill_value=0)
    elif int(year[0]) < 2000:
        df_1995 = df_1995.add(df_file, fill_value=0)
    elif int(year[0]) < 2005:
        df_2000 = df_2000.add(df_file, fill_value=0)
    elif int(year[0]) < 2010:
        df_2005 = df_2005.add(df_file, fill_value=0)
    elif int(year[0]) < 2016:
        df_2010 = df_2010.add(df_file, fill_value=0)

    # append to df containing all the years
    df_all = df_all.add(df_file, fill_value=0).astype(int)


# write everything to csv
df_1990.to_csv(category + '_1990.csv', encoding='utf-8')
df_1995.to_csv(category + '_1995.csv', encoding='utf-8')
df_2000.to_csv(category + '_2000.csv', encoding='utf-8')
df_2005.to_csv(category + '_2005.csv', encoding='utf-8')
df_2010.to_csv(category + '_2010.csv', encoding='utf-8')

df_all.to_csv(category + '_all_years.csv', encoding='utf-8')

