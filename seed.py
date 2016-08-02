from __future__ import division

import json
import math
import mistune
import nltk
import os
import psycopg2
import re
import string
import sys
import urlparse

from bs4 import BeautifulSoup
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.tokenize import word_tokenize

urlparse.uses_netloc.append("postgres")

url = urlparse.urlparse(os.environ["DATABASE_URL"])
conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
cur = conn.cursor()

cur.execute("""
    drop schema public cascade;
    create schema public;
""")

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
    stemmed = [stemmer.stem(t) for t in lang_filtered]

    is_word = lambda x: re.match('[a-zA-z]+\Z',x) != None
    is_tick = lambda x: x != "`" and x != "``" and x != "```"
    words = filter(is_word,stemmed)
    words = filter(is_tick,words)

    return words


if __name__ == '__main__':
    nltk.download('punkt')
    nltk.download('stopwords')

    for category in ["impl", "prod", "test"]:
        cur.execute("CREATE TABLE {:s}_words(id serial primary key, word varchar not null, count int);".format(category))

        print "Making category {:s}".format(category)

        fname = category + ".txt"
        lex_words = parse_from_file(fname)
        weighted_words = dict(Counter(lex_words))

        print "Read {:d} words from {:s}".format(len(lex_words),fname)

        for word, weight in weighted_words.iteritems():
            print "Updating {:s}, with weight {:d}".format(word,weight)

            cur.execute("INSERT INTO {:s}_words (word,count) VALUES (\'{:s}\',{:d})".format(category,word,weight))
    conn.commit()
    conn.close()
