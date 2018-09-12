import os
import csv
import spacy
spacy.load('en_core_web_sm')
from spacy.lang.en import English
from spacy.parts_of_speech import ADV, ADJ

os.chdir("/Users/moarplease/Desktop/SOCC/raw")
filename = 'comment_text.csv'
test = 'test.csv'
parser = English()

nlp = spacy.load('en')



#I made a csv with just the comments text column from the file in the SOCC corpus

with open(filename, 'r') as f:
    reader = csv.reader(f)
    your_list = list(reader)

#flatten the list
flat_list = [item for sublist in your_list for item in sublist]


tokens = []
lemma = []
pos = []
freq = 0

for comment in flat_list:
    for doc in nlp.pipe(comment, batch_size=50,
                        n_threads=3):
        if doc.is_parsed:
            tokens.append([n.text for n in doc])
            lemma.append([n.lemma_ for n in doc])
            pos.append([n.pos_ for n in doc])
        else:
        # to make sure the lists will line up (have the same number of items)
            tokens.append(None)
            lemma.append(None)
            pos.append(None)

#flatten these lists
pos = [item for sublist in pos for item in sublist]
tokens = [item for sublist in tokens for item in sublist]


for index, part in enumerate(pos):
    # for each adverb
    if part == 'ADV':
        x = index
        # if the next word is adj and ends in -ly
        if pos[index+1] == 'ADJ':
            if tokens[index][-2:] == 'ly':
                # count it
                freq = freq + 1
                print(tokens[index])
                print(tokens[index+1])

print(freq)


