#!/usr/bin/env python
# coding: utf-8

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize, sent_tokenize
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

nltk.download('stopwords')
nltk.download('punkt')


#############################################
#### ---- Read input text from URL  ---- ####
#############################################

#### ---- 0) Read contents from either file or Web URL  ---- ####
def read_file_or_web_contents(file_or_url_string):
    if "http" in file_or_url_string:
        print(">>> content source is Web HTTP/HTTPS URL: " + file_or_url_string)
        article_content = read_contents_web_wiki(file_or_url_string)
    else:
        # File (assuming file if non Web URL)
        print(">>> content source is a File: " + file_or_url_string)
        article_content = read_article(file_or_url_string)

    return article_content

#### ---- 0) Read contents from Web URL  ---- ####
def read_contents_web_wiki(url_string):
    # fetching the content from the URL
    #fetched_data = urllib.request.urlopen('https://en.wikipedia.org/wiki/20th_century')
    fetched_data = urllib.request.urlopen(url_string)

    article_read = fetched_data.read()

    # parsing the URL content and storing in a variable
    article_parsed = BeautifulSoup.BeautifulSoup(article_read, 'html.parser')

    #returning <p> tags
    paragraphs = article_parsed.find_all('p')

    article_content = ''

    # looping through the paragraphs and adding them to the variable
    for p in paragraphs:
        article_content += p.text

    print(article_content)
    return article_content

#### ---- 0) Read contents from file  ---- ####
def read_article(file_name):
    file = open(file_name, "r")
    article_content = file.read()

    print("===== contents read in: =====")
    print(article_content)
    return article_content

#########################################
#### ---- 1.) Dictionary Table  ---- ####
#########################################
def create_dictionary_table(text_string) -> dict:

    # removing stop words
    stop_words = set(stopwords.words("english"))

    words = word_tokenize(text_string)

    # reducing words to their root form
    stem = PorterStemmer()

    # creating dictionary for the word frequency table
    frequency_table = dict()
    for wd in words:
        wd = stem.stem(wd)
        if wd in stop_words:
            continue
        if wd in frequency_table:
            frequency_table[wd] += 1
        else:
            frequency_table[wd] = 1

    return frequency_table

#########################################
#### ---- 2.) Sentecnes Scores  ---- ####
#########################################


def calculate_sentence_scores(sentences, frequency_table) -> dict:

    # algorithm for scoring a sentence by its words
    sentence_weight = dict()

    for sentence in sentences:
        sentence_wordcount = (len(word_tokenize(sentence)))
        sentence_wordcount_without_stop_words = 0
        for word_weight in frequency_table:
            if word_weight in sentence.lower():
                sentence_wordcount_without_stop_words += 1
                if sentence[:7] in sentence_weight:
                    sentence_weight[sentence[:7]
                                    ] += frequency_table[word_weight]
                else:
                    sentence_weight[sentence[:7]
                                    ] = frequency_table[word_weight]

        sentence_weight[sentence[:7]] = sentence_weight[sentence[:7]
                                                        ] / sentence_wordcount_without_stop_words

    return sentence_weight

########################################
#### ---- 3.) Average Weights  ---- ####
########################################


def calculate_average_score(sentence_weight) -> int:

    # calculating the average score for the sentences
    sum_values = 0
    for entry in sentence_weight:
        sum_values += sentence_weight[entry]

    # getting sentence average value from source text
    average_score = (sum_values / len(sentence_weight))

    return average_score

################################
#### ---- 4.) Summary ---- #####
################################


def get_article_summary(sentences, sentence_weight, threshold):
    sentence_counter = 0
    article_summary = ''

    for sentence in sentences:
        if sentence[:7] in sentence_weight and sentence_weight[sentence[:7]] >= (threshold):
            article_summary += " " + sentence
            sentence_counter += 1

    return article_summary

#########################################
#### ---- 5.) Dictionary Table  ---- ####
#########################################


def run_article_summary(article):

    # creating a dictionary for the word frequency table
    frequency_table = create_dictionary_table(article)

    # tokenizing the sentences
    sentences = sent_tokenize(article)

    # algorithm for scoring a sentence by its words
    sentence_scores = calculate_sentence_scores(sentences, frequency_table)

    # getting the threshold
    threshold = calculate_average_score(sentence_scores)

    # producing the summary
    article_summary = get_article_summary(
        sentences, sentence_scores, 1.5 * threshold)

    return article_summary


#############################################
#### -------------- main --------------- ####
#############################################
if __name__ == '__main__':
    #### ---- Test data ----
    #file_or_url_string = 'https://en.wikipedia.org/wiki/20th_century'
    #file_or_url_string = './wiki-contents.txt'
    #file_or_url_string = './fb.txt'
    #file_or_url_string = './multiline-data.txt'
    file_or_url_string = args.dataFile
    
    article_content = read_file_or_web_contents(file_or_url_string)
    #article_content = read_contents_web_wiki(file_or_url_string)
    
    summary_results = run_article_summary(article_content)
    
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Summarize Text: ")

    print(summary_results)
