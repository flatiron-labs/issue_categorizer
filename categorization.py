from __future__ import division
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
from collections import Counter
from nltk.stem.porter import *
from sklearn.feature_extraction.text import TfidfVectorizer


def setup():
    nltk.download('punkt')
    nltk.download('stopwords')

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


def parse_from_file(filename):
    with open(filename) as f:
        md = mistune.markdown(f.read().decode('utf-8'))
        soup = BeautifulSoup(md, 'html.parser')
        data = soup.get_text()
    return parse_text(data)

#A word is a string, a lexicon is a collection of 2 tuples: (str,count)
def is_member_of(word,lex):
    if lex[word] > 0:
        return 1
    else:
        return 0

#def weight(word,lex):
#    return math.sqrt(lex[word])/(len(lex) + 1)

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
    def __init__(self,stems):
        self._stems = dict(Counter(stems))

    def has_member(self,s):
        if s in self._stems:
            return 1
        else:
            return 0

    def weight(self, word):
        if self.has_member(word):
            return math.sqrt(self._stems[word]/(len(self._stems) + 1))
        else:
            return 0
        



if __name__ == '__main__':
    #issue_text = "I completed the lab using the 'learn -b' command from the CLI and got all tests passing. Then I ran just 'learn' to check it in and it said \"Owner should be able to go on a bike ride\" fails, even though this was done and repeated within seconds of each other. I'll open a PR for the code in a moment."
    #issue_text = "Use of 'optional' here is confusing because recommended reading has section which refers to \"Optional Arguments\" (defined in method signature with *) which are different than \"Arguments with Default Values\" (also covered in the recommended reading) which is what we appear to be going for here. "
    #issue_text = "The video and the readme can really be broken in half.\nFirst, the mechanics of defining methods.\nThen arguments."
    #issue_text = "Wouldn't this example method stop removing apples from the basket when there were 5 apples in the basket and 5 taken out instead of continuing until all the apples were removed from the basket? Because at that point the condition for continuing to iterate would be false---5 is not less than 5. Or am I just misunderstanding something? Thanks!"
    #issue_text = "Description for #non_sailors spec is wrong and should be people who are not captains of sail boats"
    #issue_text = """
    #Break apart text readings into separate lessons and relink them in learn as separate repos.
    #"""
    issue_text = """
    Update CocoaPods, only Specta/Expecta needed

    Expecta not imported into Spec file

    Advanced section introduces NSError. Is this too early? Nice link to the NSHipster blog post.

    Add objectives and update for consistent style.
    """

    issue_text = """
    "i reached the first lab lesson, but i find that the \"open\" tab is greyed and cannot be clicked to open the CLI in introus. when i manually open nitrous CLI IDE, i can't find the lesson folder under the lab folder, and i keep getting message \"You don't appear to be in a Learn lesson's directory. Please cd to an appropriate directory and try again.\"",
    """

    setup()
    impl = Lexicon(parse_from_file("impl.txt"))
    prod = Lexicon(parse_from_file("prod.txt"))
    test = Lexicon(parse_from_file("test.txt"))

    #lexicons = [impl,prod,test]
    D = set([impl,prod,test])
    
    print("Testing issue \"{:s}...\"".format(issue_text[:20]))

    issue_words = parse_text(issue_text)

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

    category = max(issue_scores, key=issue_scores.get)
    print("Issue is most likely a(n) {:s} issue".format(category))
    print(issue_scores)
    #embed()

