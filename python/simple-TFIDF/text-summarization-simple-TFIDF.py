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

###################################
#### ---- Arugment setup  ---- ####
###################################

parser = ArgumentParser()

#### ---- data file ----
# parser.add_argument("-d", "--data", dest="dataFile", help="read data from", metavar="FILE")
parser.add_argument("-d", "--data", dest="dataFile", help="read data from either a file or Web URL")
parser.add_argument("-o", "--out", dest="outFile", help="write summary as output to a file")
parser.add_argument("-a", "--alpha", dest="alpha", help="threshold alpha (multiplier), default 1.15")

#### ---- Unit Test or not ----
feature_parser = parser.add_mutually_exclusive_group(required=False)
feature_parser.add_argument("-t", "--test", dest='unitTest', action='store_true')

parser.set_defaults(feature=False)

args = parser.parse_args()

#### ---- Extract dataFile value ----
file_or_url_string = ""
if args.dataFile is not None:
    print('The data file name is {}'.format(args.dataFile))
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> data file=" + args.dataFile)
    file_or_url_string = args.dataFile
else:
    if args.unitTest:
        print("--- Unit Testing ----")
    else:
        print('*** ERROR: No data file provided! ... Abort!')
        sys.exit()

#### ---- Extract outFile value ----
out_file_string = "text-summary-out.txt"
if args.outFile is not None:
    print('The out file name is {}'.format(args.outFile))
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> out file=" + args.outFile)
    out_file_string = args.outFile

#### ---- Extract alpha value ----
alpha = 1.15
if args.alpha is not None:
    print('The alpha value is {}'.format(args.alpha))
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> alpha=" + args.alpha)
    alpha = args.alpha

########################
########################
#### ---- main ---- ####
########################
########################

nltk.download('stopwords')
nltk.download('punkt')


#############################################
#### ---- Read input text from URL  ---- ####
#############################################

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
    for p in paragraphs:
        print(p.text)
        p_text = p.text
        if p_text and p_text.strip():
            article_content.extend(p_text.strip().split(". "))

    print("===== contents read in: =====")
    print("------- URL article being read in: " + url_string)
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

    print("===== contents read in: =====")
    print("------- Text article being read in: " + file_name)
    print(article)

    return article


#################################################
#### ---- 0.) Conver Strings to a String---- ####
#################################################
def convert_array_string_to_one_string(article_contents):
    text_string = ''
    for line in article_contents:
        text_string = text_string + " " + line

    print("convert lines into one long line for create_dictionary_table(text_string) to consume:")
    print(text_string)

    return text_string


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
                    sentence_weight[sentence[:7]] += frequency_table[word_weight]
                else:
                    sentence_weight[sentence[:7]] = frequency_table[word_weight]

        sentence_weight[sentence[:7]] = sentence_weight[sentence[:7]] / sentence_wordcount_without_stop_words

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

def generate_summary(file_or_url_string, out_file_string, alpha):
    sentences = read_file_or_web_contents(file_or_url_string)
    article = convert_array_string_to_one_string(sentences)

    # creating a dictionary for the word frequency table
    frequency_table = create_dictionary_table(article)

    # tokenizing the sentences
    #    sentences = sent_tokenize(article)

    # algorithm for scoring a sentence by its words
    sentence_scores = calculate_sentence_scores(sentences, frequency_table)

    # getting the threshold
    threshold = calculate_average_score(sentence_scores)
    print("threshold=" + str(threshold))


    # producing the summary
    summarize_text = get_article_summary(
        sentences, sentence_scores, float(alpha) * float(threshold))

    # Step 5 - Now, output the summarize texr
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Summarized Text: ")
    print(summarize_text)

    # Step 6 - Output to a file
    with open(out_file_string, 'w') as outfile:
        for item in summarize_text:
            outfile.write(item)
            #outfile.write("%s" % item)

    return summarize_text


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
        generate_summary(file_or_url_string)


#############################################
#### -------------- main --------------- ####
#############################################
if __name__ == '__main__':

    if args.unitTest:
        test_cases()
    else:
        summary_results = generate_summary(file_or_url_string, out_file_string, alpha)

