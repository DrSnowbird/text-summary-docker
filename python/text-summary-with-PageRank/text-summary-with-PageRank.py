#!/usr/bin/env python
# coding: utf-8

import bs4 as BeautifulSoup
import urllib.request
import sys

import argparse
from argparse import ArgumentParser

###################################
#### ---- Arugment setup  ---- ####
###################################

parser = ArgumentParser()

#### ---- data file ----
# parser.add_argument("-d", "--data", dest="dataFile", help="read data from", metavar="FILE")
parser.add_argument("-d", "--data", dest="dataFile", help="read data from either a file or Web URL")

#### ---- Unit Test or not ----
feature_parser = parser.add_mutually_exclusive_group(required=False)
feature_parser.add_argument("-t", "--test", dest='unitTest', action='store_true')
parser.set_defaults(feature=False)

args = parser.parse_args()
if args.dataFile is not None:
    print('The data file name is {}'.format(args.dataFile))
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> data file=" + args.dataFile)
else:
    if args.unitTest:
        print("--- Unit Testing ----")
    else:
        print('*** ERROR: No data file provided! ... Abort!')
        sys.exit()

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


####################################################
#### ---- Read input text from URL or file ---- ####
####################################################

#### ---- 0) Read contents from either file or Web URL  ---- ####
def read_file_or_web_contents(file_or_url_string):
    if "http" in file_or_url_string:
        print(">>> content source is Web HTTP/HTTPS URL: " + file_or_url_string)
        article_content = read_contents_web_wiki(file_or_url_string)
    else:
        # File (assuming file if non Web URL)
        print(">>> content source is a File: " + file_or_url_string)
        article_content = read_article_single_or_multi_lines(file_or_url_string)

    return article_content


#### ---- 0) Read contents from Web URL  ---- ####
def read_contents_web_wiki(url_string):
    # fetching the content from the URL
    # fetched_data = urllib.request.urlopen('https://en.wikipedia.org/wiki/20th_century')
    fetched_data = urllib.request.urlopen(url_string)

    article_read = fetched_data.read()

    # parsing the URL content and storing in a variable
    article_parsed = BeautifulSoup.BeautifulSoup(article_read, 'html.parser')

    # returning <p> tags
    paragraphs = article_parsed.find_all('p')

    article_content = []

    # looping through the paragraphs and adding them to the variable
    print("---- preparing paragraph: \n")
    for p in paragraphs:
        print(p.text)
        p_text = p.text
        if p_text and p_text.strip():
            article_content.extend(p_text.strip().split(". "))

    print(article_content)
    return article_content


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


#### ----Sentence Similarity ---- ####
def process_sentences(article):
    sentences = []
    for sentence in article:
        print(sentence)
        sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))

    # why pop the last sentence?
    sentences.pop()

    return sentences

#### ----Sentence Similarity Matrix---- ####
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
def generate_summary(file_or_url_string, top_n=5):

    stop_words = stopwords.words('english')
    summarize_text = []

    # Step 1 - Read text anc split it
    # article = read_article(file_or_url_string)

    article = read_file_or_web_contents(file_or_url_string)
    # article = read_article_single_or_multi_lines(file_or_url_string)

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


def test_cases():
    files=[]
    files.append("https://en.wikipedia.org/wiki/20th_century")
    files.append("./wiki-contents.txt")
    files.append("./fb.txt")
    files.append("./multiline-data.txt")

    #file_or_url_string = 'https://en.wikipedia.org/wiki/20th_century'
    #file_or_url_string = './wiki-contents.txt'
    #file_or_url_string = './fb.txt'
    #file_or_url_string = './multiline-data.txt'

    for file_or_url_string in files:
        print("\n\n\n######## Test with files or URL: " + file_or_url_string)
        generate_summary(file_or_url_string, 2)


##############################################
#### -------------- tests --------------- ####
##############################################
def test_cases():
    files = []
    files.append("https://en.wikipedia.org/wiki/20th_century")
    files.append("../../data/wiki-contents.txt")
    files.append("../../data/msft.txt")
    files.append("../../data/multiline-data.txt")

    for file_or_url_string in files:
        print("\n\n\n######## Test with files or URL: " + file_or_url_string)
        generate_summary(file_or_url_string, 2)

    # Step 5 - Offcourse, output the summarize texr
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Summarize Text: ")
    print(summarize_text)
    
    return summarize_text


##############################################
#### -------------- tests --------------- ####
##############################################
def test_cases():
    files=[]
    files.append("https://en.wikipedia.org/wiki/20th_century")
    files.append("../../data/wiki-contents.txt")
    files.append("../../data/msft.txt")
    files.append("../../data/multiline-data.txt")

    for file_or_url_string in files:
        print("\n\n\n######## Test with files or URL: " + file_or_url_string)
        generate_summary(file_or_url_string, 2)
        
#############################################
#### -------------- main --------------- ####
#############################################
if __name__ == '__main__':
    
    file_or_url_string = args.dataFile

    if args.unitTest:
        test_cases()
    else:
        summary_results = generate_summary(file_or_url_string, 2)
        