"""
Program to find the oxymoronic pairs from the adverbly adjectives data which
contains adverb-adjective pairs from the COCA, CORE and TIME corpora.

The NRC VAD dictionary or SentiWordNet 3.0 can be used to generate the polarity
differences between the adverbs and the adjectives. Functions exist to do this
which take a pandas DataFrame (along with the name of the adverb and adjective
columns) as input.

@author Vasundhara Gautam
"""


import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from difflib import get_close_matches as gcm
from itertools import chain
from nltk.corpus import sentiwordnet as swn
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import WordNetError


# Imports and pre-processing

# You will likely need to replace the file paths for COCA, CORE and TIME data, as well as the VAD dict

coca_file = '~/sfuvault/Discourse-Lab/Data/Adverbly_adjectives/COCA/all_years/all_years.csv'
core_file = '~/sfuvault/Discourse-Lab/Data/Adverbly_adjectives/CORE/data/CORE_allgenres.xlsx'
time_file = ''

VAD_dict_file = '~/Documents/University/Semester6/USRA/NRC-VAD-Lexicon-Aug2018Release/OneFilePerDimension/v-scores.txt'
VAD_dict = pd.read_table(VAD_dict_file, header=None, names=['VAD_word', 'VAD_valence'])


# Function definitions


"""
Function to use WordNet to find adjectives from input adverb
E.g., if 'terribly' is not found in the VAD dictionary, look for the valence of 'terrible'
"""
def advToAdj(adv):
    try:
        possible_adjectives = [k.name() for k in chain(*[j.pertainyms() for j in chain(*[i.lemmas() for i in wn.synsets(adv)])])]
    except WordNetError:
        return None
    if len(possible_adjectives) == 0:
        return None
    closest_matches = gcm(adv,possible_adjectives)
    if len(closest_matches) == 0:
        return None
    return closest_matches[0]

"""
SWN polarity of an input term with a certain part of speech is calculated by the
best performing method outlined in Guerini et al for regression using SWN 3.0 -
harmonic weighted sums of all the subjective senses of a word.
"""
def calculateSWNPolarity(term, pos, how):
    # Get synsets for all the senses given a specified part of speech
    try:
        synsets = list(swn.senti_synsets(term, pos=pos))
    except WordNetError:
        return None
    # Throw out entirely objective synsets
    for i in synsets:
        if i.obj_score() == 1:
            synsets.remove(i)
    if len(synsets) == 0:
        return None
    # Sort positive and negative scores in descending order
    #   "word’s prior polarity might be more related to its posterior polarities score,
    #   rather than to sense frequencies"
    # So giving more relevance to more "valenced" senses
    pos = sorted([i.pos_score() for i in synsets], reverse=True)
    neg = sorted([i.neg_score() for i in synsets], reverse=True)
    pos_harmonic = 0
    neg_harmonic = 0

    if how == 'harmonic':
        # Weighting them with a harmonic series
        for i in range(len(pos)):
            pos_harmonic += pos[i]/(i+1)
            neg_harmonic += neg[i]/(i+1)
    else:
        # Weighting them with a geometric series
        for i in range(len(pos)):
            pos_harmonic += pos[i]*(0.5**i)
            neg_harmonic += neg[i]*(0.5**i)

    # Absolute maximum of the scores, assigning a negative to indicate negativity
    return pos_harmonic if pos_harmonic >= neg_harmonic else -neg_harmonic

"""
Merging on adverbs and then adjectives in the pairs.
First priority for adverb valence values is for adverbs that exist in the dictionary,
then I try to convert the missing ones to adjectives.
Only valence scores are used from the VAD dictionary
"""
def oxymoronsByVAD(df, adv_col, adj_col):
    df = df.dropna(axis=1)
    df_adv = df.merge(VAD_dict, how='left', left_on=adv_col, right_on='VAD_word')
    df_merged = df_adv.merge(VAD_dict, how='left', left_on=adj_col, right_on='VAD_word')

    null_adverbs = df_merged[df_merged['VAD_word_x'].isnull()]
    null_adverbs = null_adverbs.drop('VAD_word_x', axis=1).drop('VAD_word_y', axis=1).drop('VAD_valence_x', axis=1).drop('VAD_valence_y', axis=1)

    null_adverbs['Adv2Adj'] = null_adverbs[adv_col].apply(advToAdj)
    adv2adj_merged = null_adverbs.merge(VAD_dict, how='left', left_on='Adv2Adj', right_on='VAD_word')
    adv2adj_merged = adv2adj_merged.merge(VAD_dict, how='left', left_on=adj_col, right_on='VAD_word').dropna()

    # Concat-ing the adverbs and adverbs->adjectives data valence values together
    df_VAD = pd.DataFrame(df_merged.dropna())
    df_VAD = pd.concat([df_VAD, adv2adj_merged.dropna()])

    df_VAD['diff'] = (df_VAD['VAD_valence_x'].sub(df_VAD['VAD_valence_y'])).abs()
    df_VAD.sort_values('diff', ascending=False, inplace=True)
    return df_VAD

"""
Merging on adverbs and then adjectives in the pairs.
The polarity of a word is calculated using the calculateSWNPolarity function.
"""
def oxymoronsBySWN(df, adv_col, adj_col, weighting_type):
    df = df.dropna(axis=1)
    adv = pd.DataFrame(df[adv_col].drop_duplicates())
    adj = pd.DataFrame(df[adj_col].drop_duplicates())

    adv['SWN_polarity'] = adv[adv_col].apply(calculateSWNPolarity, pos='r', how=weighting_type)
    adj['SWN_polarity'] = adj[adj_col].apply(calculateSWNPolarity, pos='a', how=weighting_type)

    df_adv = df.merge(adv, how='left', on=adv_col)
    df_adj = df_adv.merge(adj, how='left', on=adj_col)
    df_SWN = pd.DataFrame(df_adj.dropna())
    df_SWN['diff'] = (df_SWN['SWN_polarity_x'].sub(df_SWN['SWN_polarity_y'])).abs()
    df_SWN.sort_values('diff', ascending=False, inplace=True)
    return df_SWN


# Computing polarity differences


# COCA data

coca_raw = pd.read_csv(coca_file)

# COCA-VAD
coca_VAD = oxymoronsByVAD(coca_raw, 'Adv', 'Adj')
coca_VAD.to_csv('coca_VAD_full.csv')
coca_VAD[coca_VAD['diff'] > coca_VAD['diff'].quantile()].to_csv('coca_VAD_50percentile.csv')

# COCA-SWN
coca_SWN = oxymoronsBySWN(coca_raw, 'Adv', 'Adj', 'harmonic')
coca_SWN.to_csv('harmonic_coca_SWN_full.csv')
coca_SWN[coca_SWN['diff'] > coca_SWN['diff'].quantile()].to_csv('harmonic_coca_SWN_50percentile.csv')

coca_SWN = oxymoronsBySWN(coca_raw, 'Adv', 'Adj', 'geometric')
coca_SWN.to_csv('geometric_coca_SWN_full.csv')
coca_SWN[coca_SWN['diff'] > coca_SWN['diff'].quantile()].to_csv('geometric_coca_SWN_50percentile.csv')

# CORE data

core_raw = pd.read_excel(core_file)
core_combination = core_raw.rename_axis('Combination').reset_index()
split = core_combination['Combination'].str.split(n=1, expand=True)
core_combination['Adv'] = split[0].str.lower()
core_combination['Adj'] = split[1].str.lower()

# CORE-VAD data
core_VAD = oxymoronsByVAD(core_combination, 'Adv', 'Adj')
core_VAD.to_csv('core_VAD_full.csv')
core_VAD[core_VAD['diff'] > core_VAD['diff'].quantile()].to_csv('core_VAD_50percentile.csv')

# CORE-SWN data
core_SWN = oxymoronsBySWN(core_combination, 'Adv', 'Adj', 'harmonic')
core_SWN.to_csv('harmonic_core_SWN_full.csv')
core_SWN[core_SWN['diff'] > core_SWN['diff'].quantile()].to_csv('harmonic_core_SWN_50percentile.csv')

core_SWN = oxymoronsBySWN(core_combination, 'Adv', 'Adj', 'geometric')
core_SWN.to_csv('geometric_core_SWN_full.csv')
core_SWN[core_SWN['diff'] > core_SWN['diff'].quantile()].to_csv('geometric_core_SWN_50percentile.csv')

# TIME

# TIME-VAD

# TIME-SWN
