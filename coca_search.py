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

    # for the OLD POS FILES
    # btw the year 2012 has 2 files (1 old, 1 new)
    if not filename[:4].isdigit():
        df_file = pd.read_csv(filename, encoding='latin1', skiprows=[0], sep='\t', error_bad_lines=False, quoting=3,
                              lineterminator='\r', header=None, index_col=None)
        df_file.columns = ['word', 'lemma', 'pos']
        df_file = df_file[['word', 'pos']]

        # trim out the first character
        df_file['word'] = df_file['word'].str[1:]

    # for the NEW POS FILES
    if filename[:4].isdigit():
        # newer POS files have different columns
        df_file = pd.read_csv(filename, encoding='latin1', skiprows=[0], sep='\t', error_bad_lines=False, quoting=3,
                              lineterminator='\r', header=None, index_col=None)
        df_file.columns = ['index', 'textid', 'word', 'lemma', 'pos']
        df_file = df_file[['word', 'pos']]

    # lowercase
    df_file['word'] = df_file['word'].str.lower()

    # add a column for the next word and POS
    df_file["nextword"] = df_file["word"].shift(-1)
    df_file["nextpos"] = df_file['pos'].shift(-1)

    # filter for rows where the POS = adv (r*), word ends in -ly followed by NEXTPOS = adj (j*)
    # NOTE: in ambiguity tag pairs the r*/j* will be the first tag
    # filter for slashes or hyphens
    df_file = df_file[(df_file['pos'].str[0] == 'r') & (df_file['word'].str[-2:] == 'ly') & (~df_file['word'].str.contains("-|/",  na=False))
                      & (df_file['nextpos'].str[0] == 'j') & (~df_file['nextword'].str.contains("-|/",  na=False))]

    # add a column for the adv adj pair
    df_file['pair'] = df_file['word'] + " " + df_file['nextword']
    df_file = df_file.drop(columns=['word', 'pos', 'nextword', 'nextpos'], axis=1)

    # get the count for each pair
    #df_file['count'] = df_file.groupby('pair', as_index=False)['pair'].transform(lambda s: s.count())
    #df_file['freq'] = df_file.groupby(["pair"]).count()
    df_file['freq'] = df_file.groupby('pair')['pair'].transform('count')

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


# total counts for each period
with open(category + "_totals" + ".txt", "w+") as f:
    f.write("1990: " + str(df_1990['freq'].sum()) + "\n")
    f.write("1995: " + str(df_1995['freq'].sum()) + "\n")
    f.write("2000: " + str(df_2000['freq'].sum()) + "\n")
    f.write("2005: " + str(df_2005['freq'].sum()) + "\n")
    f.write("2010: " + str(df_2010['freq'].sum()) + "\n")

