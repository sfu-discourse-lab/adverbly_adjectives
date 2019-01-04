import os
import csv
import spacy
spacy.load('en_core_web_sm')
#from spacy.lang.en import English
#from spacy.parts_of_speech import ADV, ADJ
from collections import defaultdict


#parser = English()
nlp = spacy.load('en')

os.chdir("/Users/moarplease/Desktop/SOCC/raw")

# NAME OF COMMENT TEXT FILE
#filename = 'comment_text.csv'
filename = 'test.csv'

#I made a csv with just the comments text column from the file in the SOCC corpus

with open(filename, 'r') as f:
    reader = csv.reader(f)
    your_list = list(reader)

# flatten the list
flat_list = [item for sublist in your_list for item in sublist]

tokens = []
lemma = []
pos = []
freq = 0

for doc in nlp.pipe(flat_list, batch_size=50, n_threads=3):
    if doc.is_parsed:
        tokens.append([n.text for n in doc])
        lemma.append([n.lemma_ for n in doc])
        pos.append([n.pos_ for n in doc])
    else:
        # to make sure the indices will line up
        tokens.append(None)
        lemma.append(None)
        pos.append(None)

# flatten these lists
pos = [item for sublist in pos for item in sublist]
tokens = [item for sublist in tokens for item in sublist]

# dictionary - each key is a tuple with the advadj pair and the value is the count
my_dict = defaultdict(int)

for index, part in enumerate(pos):
    # for each adverb
    if part == 'ADV':
        x = index
        # if the next word is adj and ends in -ly
        if pos[index+1] == 'ADJ':
            if tokens[index][-2:] == 'ly':
                # count it
                freq = freq + 1
                # dict key is 'word1 word2' in lowercase
                key = tokens[index].lower() + " " + tokens[index+1].lower()
                # add to the dict
                my_dict[key] += 1
                #print(tokens[index])
                #print(tokens[index+1])

print("Freq: " +str(freq))

with open("advadj_count.txt", "w+") as f:
    f.write("Frequency: " + str(freq) + "\n")
    f.write("Filename: " + filename)

with open('advadj_dict.csv', 'w+') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in my_dict.items():
       writer.writerow([key, value])
