import pandas as pd
import os
import re
import glob

os.chdir("/Users/moarplease/Desktop/TIME results")

df_all = pd.DataFrame()
df_1920 = pd.DataFrame()
df_1930 = pd.DataFrame()
df_1940 = pd.DataFrame()
df_1950 = pd.DataFrame()
df_1960 = pd.DataFrame()
df_1970 = pd.DataFrame()
df_1980 = pd.DataFrame()
df_1990 = pd.DataFrame()
df_2000 = pd.DataFrame()


fnames = glob.glob("*.txt")

for filename in fnames:
    year = re.compile(r'\d+').findall(filename)
    df_file = pd.read_csv(filename, delim_whitespace=True, skiprows=3, index_col=0, header=None, skipfooter=2)

    if int(year[0]) < 1930:
        df_1920 = df_1920.append(df_file, ignore_index=True)


    elif int(year[0]) < 1940:
        df_1930 = df_1930.append(df_file, ignore_index=True)
    elif int(year[0]) < 1950:
        df_1940 = df_1940.append(df_file, ignore_index=True)
    elif int(year[0]) < 1960:
        df_1950 = df_1950.append(df_file, ignore_index=True)
    elif int(year[0]) < 1970:
        df_1960 = df_1960.append(df_file, ignore_index=True)
    elif int(year[0]) < 1980:
        df_1970 = df_1970.append(df_file, ignore_index=True)
    elif int(year[0]) < 1990:
        df_1980 = df_1980.append(df_file, ignore_index=True)
    elif int(year[0]) < 2000:
        df_1990 = df_1990.append(df_file, ignore_index=True)
    elif int(year[0]) < 2010:
        df_2000 = df_2000.append(df_file, ignore_index=True)
filelist = [df_1920, df_1930,df_1940,df_1950, df_1960, df_1970, df_1980, df_1990, df_2000]

for dataframe in filelist:
    dataframe.columns = ['w1', 'w2', 'count']
    dataframe["pair"] = dataframe['w1'].map(str) + ' ' + dataframe['w2']
    dataframe['total'] = dataframe['count'].groupby(dataframe['pair']).transform('sum')
    #dataframe = dataframe.drop_duplicates(subset=['pair'], keep=False)
    #df_all = df_all.append(dataframe, ignore_index=True)

df_1920 = df_1920.drop_duplicates(subset=['pair'])
df_1930 = df_1930.drop_duplicates(subset=['pair'])
df_1940 = df_1940.drop_duplicates(subset=['pair'])
df_1950 = df_1950.drop_duplicates(subset=['pair'])
df_1960 = df_1960.drop_duplicates(subset=['pair'])
df_1970 = df_1970.drop_duplicates(subset=['pair'])
df_1980 = df_1980.drop_duplicates(subset=['pair'])
df_1990 = df_1990.drop_duplicates(subset=['pair'])
df_2000 = df_2000.drop_duplicates(subset=['pair'])



#df_all['x'] = df_all['total'].groupby(df_all['pair']).transform('sum')
#df_all = df_all.drop_duplicates(subset=['pair'])

df_1920.to_csv('time' + '_1920.csv', encoding='utf-8', columns=['pair', 'total'])
df_1930.to_csv('time' + '_1930.csv', encoding='utf-8', columns=['pair', 'total'])
df_1940.to_csv('time' + '_1940.csv', encoding='utf-8', columns=['pair', 'total'])
df_1950.to_csv('time' + '_1950.csv', encoding='utf-8', columns=['pair', 'total'])
df_1960.to_csv('time' + '_1960.csv', encoding='utf-8', columns=['pair', 'total'])
df_1970.to_csv('time' + '_1970.csv', encoding='utf-8', columns=['pair', 'total'])
df_1980.to_csv('time' + '_1980.csv', encoding='utf-8', columns=['pair', 'total'])
df_1990.to_csv('time' + '_1990.csv', encoding='utf-8', columns=['pair', 'total'])
df_2000.to_csv('time' + '_2000.csv', encoding='utf-8', columns=['pair', 'total'])



#df_all.to_csv('time' + '_all_years.csv', encoding='utf-8', columns=['pair', 'x'])

