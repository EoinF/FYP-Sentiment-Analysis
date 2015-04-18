# -*- coding: latin-1 -*-

import nltk

text = "hello world €500,000"

tokens = nltk.regexp_tokenize(text, '''(?x)    #Allow verbose regexps
    ([A-Z]\.)+                  #Abbreviations
    | \w+(-\w+)*                #Words with internal hyphens
    | [\$€£]?[\d,]+(\.[\d,]+)?%?   #Currency and percentages
    | \.\.\.                    #Ellipsis
    ''')

print tokens
