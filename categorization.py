from __future__ import division
from flask import Flask
from flask import request
from flask import Response
from flask import send_from_directory
from flask import Flask, render_template

import json
import math
import nltk
import operator
import os
import psycopg2
import re
import string
import sys
import urlparse

from collections import Counter
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import *

nltk.data.path.append('./nltk_data/')
urlparse.uses_netloc.append("postgres")

db_url = os.environ.get(
    "DATABASE_URL",
    "postgres://localhost:5432/issue_categorization"
)

url = urlparse.urlparse(db_url)
conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
cur = conn.cursor()
app = Flask(__name__)

def parse_text(s):
    raw_tokenized = [word for word in word_tokenize(s)]
    punctuation = [c for c in string.punctuation]
    punc_filtered = [word.lower() for word in raw_tokenized if word not in punctuation]

    lang_filtered = [w for w in punc_filtered if not w in stopwords.words('english')]

    stemmer = PorterStemmer()
    stemmed = [stemmer.stem(t) for t in lang_filtered]

    is_word = lambda x: re.match('[a-zA-z]+\Z',x) != None
    is_tick = lambda x: x != "`" and x != "``" and x != "```"

    words = filter(is_word, stemmed)
    words = filter(is_tick, words)

    return words

def msum(f, l):
    sig = 0
    for x in l:
        sig += f(x)
    return sig

def mproduct(f, l):
    pr = 1
    for x in l:
        pr *= f(x)
    return pr

class Lexicon:
    def __init__(self,name):
        self.name = name
        cur.execute("SELECT count(*) FROM {:s}_words".format(name))
        self.size = cur.fetchone()[0]

    def has_member(self,s):
        cur.execute("SELECT * FROM {:s}_words WHERE word='{:s}';".format(self.name,s))
        result = cur.fetchall()
        if result != []:
            return True
        else:
            return False

    def get_raw_count(self,s):
        cur.execute("SELECT * FROM {:s}_words WHERE word='{:s}';".format(self.name,s))
        result = cur.fetchone()
        if result != []:
            return result[2]
        else:
            return 0


    def weight(self, word):
        if self.has_member(word) == 1:
            w = math.sqrt(self.get_raw_count(word)/(self.size + 1))
            return w
        else:
            return 0

def get_issue_category(issue, lexicons):
    impl, prod, test = lexicons
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

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path,'favicon.ico', mimetype='image/png')

@app.route('/categorize_issue',methods=['POST'])
def issue_request():
    prod = Lexicon("prod")
    impl = Lexicon("impl")
    test = Lexicon("test")

    raw_data = request.data
    if not raw_data:
        return Response("400 Bad Request")

    issue_json = json.loads(raw_data)
    return Response(get_issue_category(issue_json['issue'],(impl,prod,test)))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
