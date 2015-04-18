from analyzer import loadAllPosts, tokenizeList
from analyzer import CLEAN_HTML, REMOVE_QUOTES, LOWERCASE, STRIP_WHITESPACE, WORDNET_ONLY, REMOVE_PUNCTUATION
from analyzer import TOKENIZE_CUSTOM, TOKENIZE_ON_PUNC_WHITESPACE, TOKENIZE_ON_WHITESPACE
import nltk
import json, sys
from nltk.corpus import stopwords
import string

import timing


TOKENIZE_SETTINGS = CLEAN_HTML | REMOVE_QUOTES | LOWERCASE | STRIP_WHITESPACE | REMOVE_PUNCTUATION, TOKENIZE_CUSTOM, [stopwords.words(), string.punctuation]
MINIMUM_BIGRAM_FREQUENCY = 7

isBigrams = (len(sys.argv) > 1 and 
    (sys.argv[1] == "bigrams" or sys.argv[1] == "-b"))

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

    print "tokenizing list"
    tokens = tokenizeList(entryList, *TOKENIZE_SETTINGS)

    tokens = [t.encode("utf-8") for t in tokens if t.strip() != ""]

    if isBigrams:
        print "generating bigrams"
        headings = getBigrams(tokens, MINIMUM_BIGRAM_FREQUENCY)

    headings = list(set(headings))

    print "aggregating data..."
    output = aggregateData(entryList, headings, sentiment, prices)

    if isBigrams:
        with open("aggregatedData_bigrams.csv", "w") as f:
            f.write(output.encode("utf-8"))
    else:
        with open("aggregatedData.csv", "w") as f:
            f.write(output.encode("utf-8"))

def aggregateData(entryList, headings, sentimentData, priceData):
    aggregatedData = "%s, thread_id, post_id, date, price, posScore, negScore, objScore" % (",".join(headings))

    linevalues = len(aggregatedData.split(","))
    for entry in entryList:
        #split text into tokens
        tokens = tokenizeList([entry], *TOKENIZE_SETTINGS)

        tokens = [t.encode("utf-8") for t in tokens if t.strip() != ""]
        #Check if we need bigrams
        if (isBigrams):
            tokens = getBigrams(tokens)
        
        tokens = list(set(tokens))
        try:
            sentimenttext = ",".join(sentimentData[str(entry[1].thread_id) + ":" + str(entry[1].post_id)])
            pricetext = ",".join(priceData[str(entry[1].thread_id)])

            tokendata = ','.join([("1" if heading in tokens else "0") for heading in headings])

            newline = "\n%s,%s,%s,%s,%s" % (tokendata, entry[1].thread_id, entry[1].post_id, pricetext, sentimenttext)
            if linevalues != len(newline.split(",")):
                print newline
            aggregatedData += newline
        except:
            print "error with key %s" % (str(entry[1].thread_id) + ":" + str(entry[1].post_id))

    return aggregatedData

def getBigrams(tokens, minfrequency = 0):
    #Transform to nltk text type
    text = nltk.Text(tokens)

    fdist = nltk.FreqDist(nltk.bigrams(text))
    
    bigrams = [" ".join(s) for s in fdist if fdist[s] > minfrequency]

#    print "%d/%d bigrams used" % (len(bigrams), len(fdist.keys()))
    return bigrams

if __name__ == "__main__":
    main()
