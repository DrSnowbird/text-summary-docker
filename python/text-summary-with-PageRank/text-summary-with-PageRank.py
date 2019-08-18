#!/usr/bin/env python
# coding: utf-8

import bs4 as BeautifulSoup
import urllib.request
import sys

import argparse
from argparse import ArgumentParser

parser = ArgumentParser()
#parser.add_argument("-d", "--data", dest="dataFile", help="read data from", metavar="FILE")
parser.add_argument("-d", "--data", dest="dataFile", help="read data from either a file or Web URL")

args = parser.parse_args()
if args.dataFile is not None:
    print('The data file name is {}'.format(args.dataFile))
else:
    print('*** ERROR: No data file provided! ... Abort!')
    sys.exit()
    
print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> data file=" + args.dataFile)


import numpy as np
import networkx as nx

# To avoid corporate proxy issue, let's preload package for NLTK using Dockerfile
#
# How to manually download (pre-load) a nltk corpus, e.g., stopwords?
# 1. Go to http://www.nltk.org/nltk_data/ and download whichever data file you want
# 2. Now in a Python shell check the value of `nltk.data.path`
# 3. Choose one of the path that exists on your machine, and unzip the data files into the `corpora` subdirectory inside.
# 4. Now you can import the data `from nltk.corpus import stopwords`
# Also,
# pip3 install -m nltk download stopwords
# 
# nltk.download('stopwords')

import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance

#############################################
#### ---- Read input text from file ---- ####
#############################################

#### ---- Read article file with either a long line or multi-line contents
def read_article_single_or_multi_lines(file_name):
    article = []
    with open(file_name, "r") as file:
        for line in file:
            print(line)
            if line and line.strip():
                article.extend(line.strip().split(". "))

    print("------- article being read in: " + file_name)
    print(article)

    return article

def read_article_multi_lines(file_name):
    file = open(file_name, "r")
    article = file.readlines()
    
    print("------- article being read in: " + file_name)
    print(article)

    return article

def read_article(file_name):
    file = open(file_name, "r")
    filedata = file.readlines()
    article = filedata[0].split(". ")
    
    print("------- article being read in: " + file_name)
    print(article)
    
    return article

#### ---- Split sentences into tokens
def process_sentences(article):
    sentences = []
    for sentence in article:
        print(sentence)
        sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
    sentences.pop()

    return sentences

def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []

    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]

    all_words = list(set(sent1 + sent2))

    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)

    # build the vector for the first sentence
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1

    # build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1

    return 1 - cosine_distance(vector1, vector2)


def build_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))

    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2:  # ignore if both are same sentences
                continue
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix

###################################################################
#### ---- Algorithm: generate summary using Text PageRank ---- ####
###################################################################
def generate_summary(file_name, top_n=5):
    stop_words = stopwords.words('english')
    summarize_text = []

    # Step 1 - Read text anc split it
    #sentences = read_article(file_name)
    article = read_article_single_or_multi_lines(file_name)
    sentences = process_sentences(article)

    # Step 2 - Generate Similary Martix across sentences
    sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

    # Step 3 - Rank sentences in similarity martix
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)

    # Step 4 - Sort the rank and pick top sentences
    sentences_list = enumerate(sentences)

    ranked_sentence = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    print("Indexes of top ranked_sentence order are ", ranked_sentence)

    for i in range(top_n):
        summarize_text.append(" ".join(ranked_sentence[i][1]))

    # Step 5 - Offcourse, output the summarize texr
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Summarize Text: ")
    print(summarize_text)

#############################################
#### -------------- main --------------- ####
#############################################
if __name__ == '__main__':
    # let's begin
    generate_summary(args.dataFile, 2)