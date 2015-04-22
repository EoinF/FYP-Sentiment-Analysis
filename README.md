# FYP-Sentiment-Analysis
My Final Year Project for Integrated Computer Science. 
Written in python. 
Uses Stanford POS tagger and SentiWordNet 3.0

# Dependencies
* NLTK 3.0
* Beautiful Soup 4.3.2
* PPR csv files must be placed in folder "../PPR" relative to the repository root
* SentiWordNet 3.0 text file (Although the code could be modified to use the nltk api, which would be preferrable)
* Stanford pos tagger 3.4.1 - also requires "english-bidirectional-distsim.tagger"

# Usage

The following are guidelines for running different scripts in the project
Make sure to install all dependencies listen above before continuing

## Post Scraper

1. Install python 2.3+
2. Download Beautiful Soup 4 (Instructions found here http://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup). Make sure to get BeautifulSoup4-4.3.2!
2. Install mysql
3. Set up SQL tables "Threads" and "Posts" as described in the backup.sql files in the common folder of this repository.
4. Change the settings in common/datamanager.py to work with your sql database
5. Change the constant URL values in the postscraper.py file to the property pin pages that you want to scrape
6. Run command "python postscraper.py"
7. Note that logs are printed to "logs/scraper.log"

## Location Generator

1. Download all of the property price register csv files and place them in "../PPR" relative to this repository's root folder
2. Run locationGen.py after scraping at least 1 thread
3. Output is stored in adressIndex.json and addressLookupTable.json

## Location Matcher

1. Run locationMatcher.py after completing the previous two tasks
2. Output is stored in addressMatches.json
 
## Sentiment Analysis

1. Download StanfordPosTagger.jar
2. Run sentimentAnalysis.py after completing the previous three tasks. (Make sure at least one entry exists in addressMatches.json or nothing will happen)
3. Output is stored in sentimentAnalysis.csv
 
## Aggregating Price vs Sentiment

1. Run aggregatePriceSent.py
2. Output is stored in aggregatedData.csv

## Aggregating Unigrams, Price, and Sentiment

1. Run aggregateData.py without any arguments
2. Output is stored in aggregatedData.csv

## Aggregating Bigrams, Price and Sentiment

1. Run aggregateData.py with the argument "bigrams"
2. Output is stored in aggregatedData.csv
