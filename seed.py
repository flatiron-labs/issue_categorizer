from __future__ import division
from pg import DB
import math
from IPython import embed
import operator
import re
from bs4 import BeautifulSoup
import mistune
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk.data
import string
import sys
from collections import Counter
from nltk.stem.porter import *

db = DB(dbname='issue_categorization', port=5432)

def parse_from_file(filename):
    with open(filename) as f:
        md = mistune.markdown(f.read().decode('utf-8'))
        soup = BeautifulSoup(md, 'html.parser')
        data = soup.get_text()
    return parse_text(data)

def parse_text(s):
    raw_tokenized = [word for word in word_tokenize(s)]
    punctuation = [c for c in string.punctuation]
    punc_filtered = [word.lower() for word in raw_tokenized if word not in punctuation]

    lang_filtered = [w for w in punc_filtered if not w in stopwords.words('english')]

    stemmer = PorterStemmer()
    stemmed = []
    for token in lang_filtered:
        stemmed.append(stemmer.stem(token))

    is_word = lambda x: re.match('[a-zA-z]+\Z',x) != None
    is_tick = lambda x: x != "`" and x != "``" and x != "```"
    words = filter(is_word,stemmed)
    words = filter(is_tick,words)
    return words

if __name__ == '__main__':

    nltk.download('punkt')
    nltk.download('stopwords')

    db.query("DROP TABLE lexicons") #clear previous

    db.query("CREATE TABLE lexicons(id serial primary key, name varchar);")
    
    for category in ["impl", "prod", "test"]:
        db.query("INSERT INTO lexicons (name) VALUES (\'{:s}\');".format(category))
        db.query("DROP TABLE {:s}_words".format(category)) #clear previous
        db.query("CREATE TABLE {:s}_words(id serial primary key, word varchar not null, count int);".format(category))

        print "Making category {:s}".format(category)
        fname = category + ".txt"
        lex_words = parse_from_file(fname)
        weighted_words = dict(Counter(lex_words))
        print "Read {:d} words from {:s}".format(len(lex_words),fname)
        for word,weight in weighted_words.iteritems():
            #print "Updating {:s}, with weight {:d}".format(word,weight)
            db.insert('{:s}_words'.format(category),row={'word': word, 'count': weight})

    db.close()
