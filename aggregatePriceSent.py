from analyzer import loadFirstPosts, loadTimeRange, loadAllPosts, tokenize, tokenizeList
from analyzer import CLEAN_HTML, REMOVE_QUOTES, LOWERCASE, STRIP_WHITESPACE, WORDNET_ONLY, REMOVE_PUNCTUATION
from analyzer import TOKENIZE_CUSTOM, TOKENIZE_ON_PUNC_WHITESPACE, TOKENIZE_ON_WHITESPACE
import nltk
import json
from nltk.corpus import stopwords
import string

import timing


TOKENIZE_SETTINGS = CLEAN_HTML | REMOVE_QUOTES | LOWERCASE | STRIP_WHITESPACE | REMOVE_PUNCTUATION, TOKENIZE_CUSTOM, [stopwords.words(), string.punctuation]

def main():
    sentiment = {}
    prices = {}

    #
    #Read in existing data sources
    #
    with open("sentimentAnalysis.csv") as f:
        print f.readline()
        for line in f:
            result = line.replace('\n', '').split(",")
            key = result[0].strip() + ":" + result[1].strip()
            values = map(str.strip, result[2:])
            sentiment[key] = values

    with open("priceValues.csv") as f:
        print f.readline()
        for line in f:
            result = line.replace('\n', '').split(",")
            key = result[0].strip()
            values = map(str.strip, result[1:])
            prices[key] = values
    
    with open("addressMatches.json") as f:
       matches = json.loads(f.read())

    entryList = [p for p in loadAllPosts() if str(p[1].thread_id) in matches]

    print "aggregating data..."
    output = aggregateData(entryList, sentiment, prices)

    with open("aggregatedPriceSent.csv", "w") as f:
        f.write(output.encode("utf-8"))

def aggregateData(entryList, sentimentData, priceData):
    aggregatedData = "thread_id, post_id, date, price, posScore, negScore, objScore"
    for entry in entryList:
        #split text into tokens
        try:
            sentimenttext = ",".join(sentimentData[str(entry[1].thread_id) + ":" + str(entry[1].post_id)])
            pricetext = ",".join(priceData[str(entry[1].thread_id)])

            newline = "\n%s,%s,%s,%s" % (entry[1].thread_id, entry[1].post_id, pricetext, sentimenttext)
            aggregatedData += newline
        except:
            print "error with key %s" % (str(entry[1].thread_id) + ":" + str(entry[1].post_id))

    return aggregatedData


if __name__ == "__main__":
    main()
