from __future__ import division
import json
from flask import Flask
from flask import request
from flask import Response 
from http_parser.parser import HttpParser
from urlparse import urlparse
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
import socket

db = DB(dbname='issue_categorization', port=5432)
app = Flask(__name__)

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

def msum(f,l):
    sig = 0
    for x in l:
        sig += f(x)
    return sig

def mproduct(f,l):
    pr = 1
    for x in l:
        pr *= f(x)
    return pr

class Lexicon:
    def __init__(self,name):
        self.name = name
        self.size = db.query("SELECT count(*) from {:s}_words".format(name)).getresult()[0][0]

    def has_member(self,s):
        result = db.get_as_list("{:s}_words".format(self.name),where="word='{:s}'".format(s))
        if result != []:
            return True
        else:
            return False

    def get_raw_count(self,word):
        result = db.get_as_list("{:s}_words".format(self.name),where="word='{:s}'".format(word))
        if result != []:
            return result[0][2]
        else:
            return 0


    def weight(self, word):
        if self.has_member(word) == 1:
            w = math.sqrt(self.get_raw_count(word)/(self.size + 1))
            return w
        else:
            return 0

def get_issue_category(issue, lexicons):
    impl,prod,test = lexicons
    D = set([impl,prod,test])

    issue_words = parse_text(issue)

    prod_score = msum(lambda w : (
        len(D) * prod.weight(w) / (msum(lambda lex: lex.weight(w), D - set([prod])) + 1)
        ),issue_words)

    test_score = msum(lambda w : (
        len(D) * test.weight(w) / (msum(lambda lex: lex.weight(w), D - set([test])) + 1)
        ),issue_words)

    impl_score = msum(lambda w : (
        len(D) * impl.weight(w) / (msum(lambda lex: lex.weight(w), D - set([impl])) + 1)
        ),issue_words)


    issue_scores = {
            'test': test_score,
            'impl': impl_score,
            'prod': prod_score
            }

    return max(issue_scores, key=issue_scores.get)

@app.route('/',methods=['GET'])
def root():
    return Response("200 OK")

@app.route('/categorize_issue',methods=['POST'])
def issue_request():
    impl = Lexicon("impl")
    prod = Lexicon("prod")
    test = Lexicon("test")

    raw_data = request.data
    if not raw_data:
        return Response("400 Bad Request")

    issue_json = json.loads(raw_data)
    return Response(get_issue_category(issue_json['issue'],(impl,prod,test)))
