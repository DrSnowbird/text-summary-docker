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

import summarizer
from summarizer import SingleModel

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
        article_content = read_article_single_or_multi_lines(file_or_url_string)

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

#### ---- 0) Read contents with single (long) line or multi lines from file into multi lines  ---- ####
#### (strip out empty lines)
def read_article_single_or_multi_lines(file_name):
    article = ''
    with open(file_name, "r") as file:
        for line in file:
            print(line)
            if line and line.strip():
                for line2 in line.strip().split(". "):
                    article += line2 + "\n"

    print("------- article being read in: " + file_name)
    print(article)
    print("\n<<<< END")
    return article

#### ---- 0) Read contents from file  ---- ####
def read_article(file_name):
    file = open(file_name, "r")
    article_content = file.read()

    print("===== contents read in: =====" + file_name)
    print(article_content)
    print("\n<<<< END")
################################################################################
#### ---- Algorithm: generate summary using Bert-Extractive-Summarizer ---- ####
################################################################################
# SingleModel Options
# model = SingleModel(
#     vector_size: int # This specifies the vector size of the output of the model. If you using a hugging face model, it will automatically be set
#     hidden: int # Needs to be negative, but allows you to pick which layer you want the embeddings to come from.
#     reduce_option: str # It can be 'mean', 'median', or 'max'. This reduces the embedding layer for pooling.
#     greedyness: float # number between 0 and 1. It is used for the coreference model. Anywhere from 0.35 to 0.45 seems to work well.
# )
# 
# model(
#     body: str # The string body that you want to summarize
#     ratio: float # The ratio of sentences that you want for the final summary
#     min_length: int # Parameter to specify to remove sentences that are less than 40 characters
#     max_length: int # Parameter to specify to remove sentences greater than the max length
# )

def generate_summary(file_or_url_string):

    # ---- test data ---
    sentences = '''
The Chrysler Building, the famous art deco New York skyscraper, will be sold for a small fraction of its previous sales price.
The deal, first reported by The Real Deal, was for $150 million, according to a source familiar with the deal.
Mubadala, an Abu Dhabi investment fund, purchased 90% of the building for $800 million in 2008.
Real estate firm Tishman Speyer had owned the other 10%.
The buyer is RFR Holding, a New York real estate company.
Officials with Tishman and RFR did not immediately respond to a request for comments.
It's unclear when the deal will close.
The building sold fairly quickly after being publicly placed on the market only two months ago.
The sale was handled by CBRE Group.
The incentive to sell the building at such a huge loss was due to the soaring rent the owners pay to Cooper Union, a New York college, for the land under the building.
The rent is rising from $7.75 million last year to $32.5 million this year to $41 million in 2028.
Meantime, rents in the building itself are not rising nearly that fast.
While the building is an iconic landmark in the New York skyline, it is competing against newer office towers with large floor-to-ceiling windows and all the modern amenities.
Still the building is among the best known in the city, even to people who have never been to New York.
It is famous for its triangle-shaped, vaulted windows worked into the stylized crown, along with its distinctive eagle gargoyles near the top.
It has been featured prominently in many films, including Men in Black 3, Spider-Man, Armageddon, Two Weeks Notice and Independence Day.
The previous sale took place just before the 2008 financial meltdown led to a plunge in real estate prices.
Still there have been a number of high profile skyscrapers purchased for top dollar in recent years, including the Waldorf Astoria hotel, which Chinese firm Anbang Insurance purchased in 2016 for nearly $2 billion, and the Willis Tower in Chicago, which was formerly known as Sears Tower, once the world's tallest.
Blackstone Group (BX) bought it for $1.3 billion 2015.
The Chrysler Building was the headquarters of the American automaker until 1953, but it was named for and owned by Chrysler chief Walter Chrysler, not the company itself.
Walter Chrysler had set out to build the tallest building in the world, a competition at that time with another Manhattan skyscraper under construction at 40 Wall Street at the south end of Manhattan. He kept secret the plans for the spire that would grace the top of the building, building it inside the structure and out of view of the public until 40 Wall Street was complete.
Once the competitor could rise no higher, the spire of the Chrysler building was raised into view, giving it the title.
'''

    # Step 1 - Read text from the file
    #sentences = read_article(file_or_url_string)
    #sentences = read_file_or_web_contents(file_or_url_string)
    sentences = read_article_single_or_multi_lines(file_or_url_string)
    
    #model = SingleModel(greedyness=0.4)
    model = SingleModel()
    
    #
    result = model(sentences, min_length=60)
    summarize_text = ''.join(result)

    # Step 5 - Now, output the summarize texr
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Summarize Text: ")
    print(summarize_text)

#############################################
#### -------------- main --------------- ####
#############################################
if __name__ == '__main__':
    # let's begin
    file_or_url_string = args.dataFile
    generate_summary(file_or_url_string)