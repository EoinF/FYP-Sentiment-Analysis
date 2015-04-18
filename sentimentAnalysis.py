from analyzer import loadFirstPosts, loadAllPosts, tokenizeList
from analyzer import CLEAN_HTML, REMOVE_QUOTES, LOWERCASE, STRIP_WHITESPACE, WORDNET_ONLY, REMOVE_PUNCTUATION
from analyzer import TOKENIZE_CUSTOM, TOKENIZE_ON_PUNC_WHITESPACE, TOKENIZE_ON_WHITESPACE
import nltk
import json
import string

#Module that outputs the time this program is running for
import timing

from nltk import metrics, stem
from nltk.corpus import stopwords
from stanford import POSTagger



def main():
    swn = loadSentiwordnet("/home/eoinf/nltk_data/corpora/sentiwordnet/SentiWordNet_3.0.0.txt")
    entryList = loadAllPosts()


    with open("addressMatches.json", "r") as f:
        data = f.read();

    matches = json.loads(data).keys()
    

    print "Calculating sentiment..."
    sentimentRaw = getSentimentFromDataset(entryList, matches, swn)

    #Create a csv version of the data
    data = "thread_id, post_id, pos_score, neg_score, obj_score\n"

    for thread in sentimentRaw:
        for post in range(0, len(sentimentRaw[thread])):
            scores = sentimentRaw[thread][post]
            data += "%s, %s, %s, %s, %s\n" % (thread, post, str(scores[0]), str(scores[1]), str(scores[2]))

    #print "Saving sentiment data"
    #with open("sentimentAnalysis.csv", "w") as f:
    #    f.write(data)

def loadSentiwordnet(filename):
    allScores = {}
    swn = {}
    with open(filename, "r") as f:
        for line in f:
            #Skip commented lines
            if line.startswith("#") or line.startswith("\t"):
                continue
            #Each line is a tab delimited quintuple (POS, id, posScore, negScore, synsetTerms, gloss)
            entry = line.split("\t")
            pos, id, posScore, negScore, synsetTerms, gloss = entry

            #Get the derived terms
            synsets = synsetTerms.split(" ") #Each synset term is separated by a space
            
            #synsetTerms are in the form "word#n" where n is the number of the synset the entry belongs to
            for synset in synsets:
                synsetAndRank = synset.split("#")

                key = pos + ":" + synsetAndRank[0]
                rank = synsetAndRank[1]

                sentScores = (float(posScore), float(negScore), int(rank))
                if key in swn:
                    allScores[key].append(sentScores)
                else:
                    allScores[key] = [sentScores]

    #Calculate the mean positive, negative and objective sentiment of each word
    #using the rank to weight each score
    for key in allScores:
        synsetSum = sum([i[2] for i in allScores[key]])
        #scores[0] / scores[2] == sentiment / rank
        posMean = sum(scores[0] / scores[2] for scores in allScores[key]) / synsetSum
        negMean = sum(scores[1] /scores[2] for scores in allScores[key]) / synsetSum
        objMean = 1 - (posMean + negMean)
        swn[key] = (posMean, negMean, objMean)

    return swn

def getSentimentFromDataset(entryList, matches, swn):
    sentiment = {}

    for thread_id in matches:
        sentiment[thread_id] = []
        for entry in entryList:
            if int(entry[1].thread_id) == int(thread_id):
                print "thread %d, post %d" % (entry[1].thread_id, entry[1].post_id)

                #split text into tokens
                tokens = tokenizeList([entry], CLEAN_HTML | REMOVE_QUOTES | LOWERCASE | STRIP_WHITESPACE | REMOVE_PUNCTUATION, TOKENIZE_CUSTOM, [stopwords.words(), string.punctuation])

                postSentiment = []

                #print entry[1].content

                if raw_input("continue?(y/n)") != "y":
                    continue

                #print tokens

                try:
                    #Get the POS tag for each token in the text
                    taggedtokens = stanfordtagger.tag(tokens)
                except:    
                    #Most likely, the pos tagger ran out of memory
                    stanfordtagger = POSTagger("../stanford-postagger-2014-08-27/models/english-bidirectional-distsim.tagger",
                        "../stanford-postagger-2014-08-27/stanford-postagger-3.4.1.jar", encoding="utf-8", java_options="-mx4000m")
                    #Try tagging again
                    try:
                        taggedtokens = stanfordtagger.tag(tokens)
                    except:
                        #If it fails again, just skip this thread
                        stanfordtagger = POSTagger("../stanford-postagger-2014-08-27/models/english-bidirectional-distsim.tagger",
                            "../stanford-postagger-2014-08-27/stanford-postagger-3.4.1.jar", encoding="utf-8", java_options="-mx4000m")
                        sentiment[thread_id].append(("?", "?", "?"))
                        continue

                
                #print taggedtokens

                #Get the sentiment from each token in the post
                for [token, tag] in taggedtokens:
                    
                    #Stanford tagger uses the penn treebank project pos list

                    '''So translate the tag for use with sentiwordnet which accepts the following tags:
                       n - Noun
                       v - Verb
                       a - Adjective
                       s - Adjective Sattelite (Stanford tagger doesn't tag adjective sattelites)
                       r - Adverb
                    '''
                    
                    if tag.startswith("N"):
                        pos = "n"
                    elif tag.startswith("V"):
                        pos = "v"
                    elif tag.startswith("J"):
                        pos = "a"
                    elif tag.startswith("R"):
                        pos = "r"
                    else: 
                        pos = "none"
                    
                    if pos != "none":
                        key = pos + ":" + token.encode('utf-8')
                        if key in swn:
                            scores = swn[key]
                            postSentiment.append(scores)
                            #print "%s: %s = %s" % (token, pos, scores)

                #Get the mean sentiment for this post
                if len(postSentiment) == 0:
                    meanPos, meanNeg, meanObj = 0, 0, 0
                    print "0 matches: %s, %s" % (thread_id, entry[1].post_id)
                    print taggedtokens
                    print entry[1].content
                else:
                    meanPos = sum(scores[0] for scores in postSentiment) / len(postSentiment)
                    meanNeg = sum(scores[1] for scores in postSentiment) / len(postSentiment)
                    meanObj = sum(scores[2] for scores in postSentiment) / len(postSentiment)
                meanPostSentiment = (meanPos, meanNeg, meanObj)
                #print "mean sentiment = %s, %s, %s" % meanPostSentiment 
                sentiment[thread_id].append(meanPostSentiment)

    return sentiment


if __name__ == "__main__":
    main()
