from analyzer import loadFirstPosts
from analyzer import CLEAN_HTML
import nltk
import json
import string

from nltk.corpus import stopwords

def main():
    entryList = loadFirstPosts()
    
    addressLookup = []
    with open("addressLookupTable.json", "r") as f:
        addressLookup = json.loads(f.read())
    
    addressIndex = []
    with open("addressIndex.json", "r") as f:
        addressIndex = json.loads(f.read())

    results = {}

    #Find all matching addresses within e
    for entry in entryList:
        content = (entry[0].title + entry[1].content).decode("ascii", "ignore")
        content = " ".join(normalize(content))
        for i in range(len(addressLookup)):
            #Check all permutations of this address against the entry e
            for permutation in addressLookup[i]:
                if permutation in content:
                    if (entry[0].thread_id in results.keys()):
                        results[entry[0].thread_id].append(addressIndex[i])
                    else:
                        results[entry[0].thread_id] = [addressIndex[i]]
                        print "Matching thread %d on %s" % (entry[0].thread_id, permutation)
                    #Only need to match one of the permutations
                    break
    
    data = json.dumps(results)
    with open("addressMatches.json", "w") as f:
        f.write(data)

def normalize(s):
    clean_s = nltk.clean_html(s)
    tokens = [w for w in nltk.wordpunct_tokenize(clean_s.lower().strip()) if w not in string.punctuation and w not in stopwords.words()]
    return tokens
    

def loadAddresses(filename):
    pprFile = open(filename, "r")

    addressList = []
    for l in pprFile:
        #Trim the leading and trailing quotes and then split by the remaining quotes
        tokens = l[1:-1].split("\"")
        if len(tokens) > 3:
            address = nltk.wordpunct_tokenize(tokens[2])
            #Put all the address components into lower case
            maddress = [w.lower() for w in address] 
            addressList.append((address, maddress))
        
    return addressList[1:]


if __name__ == "__main__":
    main()
