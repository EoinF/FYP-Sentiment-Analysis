def unusual_bigrams(entryList):
    '''
    Get all the expected bigrams by analyzing the entire corpus at once
    '''

    print "Analyzing unusual bigrams from %d posts" % len(entryList)

    #Tokenize
    tokens = tokenize(entryList, 0, TOKENIZE_ON_PUNC_WHITESPACE)

    #Transform to nltk text type
    text = nltk.Text(tokens)


    fdist = nltk.FreqDist(nltk.bigrams(text))
    ebigrams = [(fdist.freq(s), s) for s in fdist if fdist[s] > 7]


    #Sort the list of expected bigrams
    ebigrams.sort(key=lambda pair: pair[1][0])

    '''
    Find all the bigram frequency distributions for each observed post
    '''

    obigrams = []

    for entry in entryList:
        entrycontent = entry[1].content
        tokens = tokenize([entry], 0, TOKENIZE_ON_PUNC_WHITESPACE)
        entrytext = nltk.Text(tokens)
        fdist = nltk.FreqDist(nltk.bigrams(entrytext))
        postbigrams = [(fdist[s], s) for s in fdist]
        postbigrams.sort(key=lambda pair: pair[1][0])

    obigrams.append(postbigrams)

    testresults = []

    print "Calculating chi square values"

    #Get the list of counts of observed bigrams vs expected bigrams
    for e in ebigrams:
        observed = [(getObservedValue(e, postbigrams) + 1) for postbigrams in obigrams]

    expected = [(int(e[0] * len(postbigrams)) + 1) for postbigrams in obigrams]

    #Perform the chi squared test for this bigram
    testresults.append((e[1], scipy.stats.chisquare(np.array(observed), np.array(expected))))


    for t in testresults:
        print t

def getObservedValue(e, obigrams):
    for o in obigrams:
        if e[1] == o[1]:
            return o[0]
    return 0
                                                                
