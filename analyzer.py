#!/usr/bin/python
# -*- coding: latin-1 -*-

import os, errno
import sys, inspect
import logging
import nltk
import time, datetime

from bs4 import BeautifulSoup, NavigableString, Comment
from nltk.corpus import wordnet

import string

'''
Definitions for post modifiers
'''
USER_CHOICE = 0x1
CLEAN_HTML = 0x10
REMOVE_QUOTES = 0x100
LOWERCASE = 0x1000
STRIP_WHITESPACE = 0x10000
WORDNET_ONLY = 0x100000
REMOVE_PUNCTUATION = 0x1000000

'''
Definitions for tokenizers
'''
USER_CHOICE = 0x1
TOKENIZE_ON_PUNC_WHITESPACE = 0x10
TOKENIZE_ON_WHITESPACE = 0x100
TOKENIZE_CUSTOM = 0x1000

DEFAULT_TOKENIZER = TOKENIZE_ON_WHITESPACE

#Import some modules in common folder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"common")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

from datamanager import ThreadEntry, PostEntry, loadThreadPosts, postEntryExists, threadEntryExists, loadAllFirstPosts, loadFromTimeRange

print "[(thread, post)] = loadAllPosts() #Load all posts as a corpus"
def loadAllPosts():

    print "Reading all posts"
    entryList = loadFromTimeRange("1900-01-01", "3000-01-01")
    return entryList

def loadFirstPosts():
    print "Reading first posts"
    entryList = loadAllFirstPosts()
    return entryList

print "sortedEntryList = sortEntries(entryList) #Sort the list of entries"
def sortEntries(entryList):
    print "Sorting by timestamp"
    entryList.sort(key=lambda t: t[0].timestamp)
    return entryList

print "rawtext = rawText(entryList) #Join all posts into one single string"
def rawText(entryList):
    rawtext = reduce(lambda x, y: x+'\n'+y, [e[1].content for e in entryList]) 


def tokenizeList(entryList, modifierChoice=USER_CHOICE, tokenizerChoice=USER_CHOICE, filterLists = []):
    if not isinstance(entryList, list):
        print "Warning: Expected list type. Got %s" % type(entryList)
        print "in tokenizeList function"
        print "in analyzer.py"
        entryList = [entryList]

    tokens = []
       
    f_tokenize = lambda x: [x]

    #Modifications applied to individual posts
    if modifierChoice == USER_CHOICE:
        modifierChoice = getModifierChoice()

    #Choose the tokenizer function to use
    if tokenizerChoice == USER_CHOICE:
        tokenizerChoice = getTokenizerChoice()

    if TOKENIZE_CUSTOM:
        f_tokenize = lambda text: nltk.regexp_tokenize(text, '''(?x)    #Allow verbose regexps
            ([A-Z]\.)+                    #Abbreviations
            | [a-zA-Z_]+(-[a-zA-Z_]+)*    #Alphabetic words with internal hyphens
            | [\$€£][\d,]+(\.[\d,]+)?%?  #Currency and percentages
            | \.\.\.                      #Ellipsis
            ''')
    elif TOKENIZE_ON_WHITESPACE:
        f_tokenize = nltk.word_tokenize
    elif TOKENIZE_ON_PUNC_WHITESPACE:
        f_tokenize = nltk.punc_tokenize

    #if raw_input("Use segmentation (y/n)?") == "N/A":
    #    pass


    #Apply the modifier function to each entry, and then apply the tokenizer function to each entry
    tokens = [w for e in entryList for w in f_tokenize(modifyPost((e[1].content), modifierChoice))]

    #Filter out inappropriate tokens
    for fList in filterLists:
        tokens = [w for w in tokens if w.encode('utf-8') not in fList]

    #Exclude non dictionary words
    if (modifierChoice & WORDNET_ONLY) != 0:
        tokens = [w for w in tokens if len(wordnet.synsets(w.encode('utf-8'))) > 0]

    #Remove punctuation from each tokens
    if (modifierChoice & REMOVE_PUNCTUATION) != 0:
        tokens = [removePunctuation(w) for w in tokens]

    return tokens

def modifyPost(text, modifierChoice):
    if (modifierChoice & REMOVE_QUOTES) != 0:
        text = removeQuoteHtml(text)
    if (modifierChoice & CLEAN_HTML) != 0:
        text = nltk.clean_html(text)
    if (modifierChoice & LOWERCASE) != 0:
        text = text.lower()
    if (modifierChoice & STRIP_WHITESPACE) != 0:
        text = text.strip()
    return text

def removeQuoteHtml(data):
    result = ""
    soup = BeautifulSoup(data)

    #Remove all <br> tags
    for e in soup.findAll('br'):
        e.extract()
    
    for tag in soup.div.children:
        if quote_filter(tag):
            result += unicode(tag)
    
    return result

def removePunctuation(text):
    for punc in string.punctuation:
        text = text.replace(punc, "")

    return text

def quote_filter(tag):
    if type(tag) is not NavigableString and type(tag) is not Comment and tag.has_attr("class"):
        return not ("quotetitle" in tag['class'] or "quotecontent" in tag['class'])
    else:
        return True

def normalize(s):
    clean_s = nltk.clean_html(s)
    tokens = [w for w in nltk.wordpunct_tokenize(clean_s.lower().strip()) if w.encode('utf-8') not in string.punctuation and w.encode('utf-8') not in stopwords.words()]
    return tokens


def getModifierChoice():
    modifierChoice = 0 #Reset to zero modifications

    result = ''
    while result != 'ok':
        result = raw_input('''Type in one of the following numbers to apply the modification:\n
            ''' + str(CLEAN_HTML) + ''') nltk.clean_html
            ''' + str(REMOVE_QUOTES) + ''') remove quotes
            ''' + str(LOWERCASE) + ''') lowercase
            ''' + str(STRIP_WHITESPACE) + ''') strip whitepsace
            ''' + str(WORDNET_ONLY) + ''') wordnet only
            ''' + str(REMOVE_PUNCTUATION) + ''') remove punctuation
            Type "ok" when you are finished\n''')

        if result == CLEAN_HTML:
            modifierChoice |= CLEAN_HTML
        elif result == REMOVE_QUOTES:
            modifierChoice |= REMOVE_QUOTES
        elif result == LOWERCASE:
            modifierChoice |= LOWERCASE
        elif result == STRIP_WHITESPACE:
            modifierChoice |= STRIP_WHITESPACE
        elif result == WORDNET_ONLY:
            modifierChoice |= WORDNET_ONLY
        elif result == REMOVE_PUNCTUATION:
            modifierChoice |= REMOVE_PUNCTUATION
        

    return modifierChoice

def getTokenizerChoice():
    tokenizerChoice = DEFAULT_TOKENIZER

    result = ''
    while result != 'ok':
        result = raw_input('''Type in one of the following numbers to set the tokenizer:\n
            ''' + str(TOKENIZE_ON_PUNC_WHITESPACE) + ''') tokenize on punctuation and whitespace
            ''' + str(TOKENIZE_ON_WHITESPACE) + ''') tokenize on whitespace
            Type 'ok' when you are finished\n''')

        if result == TOKENIZE_ON_PUNC_WHITESPACE:
            tokenizerChoice |= TOKENIZE_ON_PUNC_WHITESPACE
        elif result == TOKENIZE_ON_WHITESPACE:
            tokenizerChoice |= TOKENIZE_ON_WHITESPACE
        elif result == TOKENIZE_CUSTOM:
            tokenizerChoice |= TOKENIZE_CUSTOM
        else:
            pass

    return tokenizerChoice

def initLogging():
    try:
        os.makedirs("logs")
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    # Setup logging to a file with timestamps
    logging.basicConfig(filename='logs/analyzer.log', format='%(asctime)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.DEBUG)


if __name__ == "__main__":
    main()
