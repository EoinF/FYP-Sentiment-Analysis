import nltk
import json
import string

def main():
    #Load all the addresses from the ppr files
    print "Loading addresses from ppr csv files"

    addressList = []
   
    #Normalize all the addresses first
    addressList.extend(loadAddresses("../PPR/PPR-2010.csv"))
    addressList.extend(loadAddresses("../PPR/PPR-2011.csv"))
    addressList.extend(loadAddresses("../PPR/PPR-2012.csv"))
    addressList.extend(loadAddresses("../PPR/PPR-2013.csv"))
    addressList.extend(loadAddresses("../PPR/PPR-2014.csv"))
    addressList.extend(loadAddresses("../PPR/PPR-2015.csv"))
    
    addressTable = [[] for _ in range(len(addressList))]

    print "Generating address index..."
    addressIndex = []
    #Generate an index of the addresses
    for a in addressList:
        addressIndex.append(a[0].decode('ascii', 'ignore'))

    print "Saving address index"

    data = json.dumps(addressIndex)
    with open("addressIndex.json", "w") as f:
            f.write(data)

    #Create a lookup table of addresses
    print "Generating lookup values for %d items..." % len(addressList)

    #For each address, keep the first 2 parts of the address and make different permutations of the other parts
    for i in range(len(addressList)):
        addressTokens = addressList[i][1]

        baseAddress = ' '.join(addressTokens[:2])

        for p in getPermutations(baseAddress, addressTokens[2:]):
            #Also include permutations with abbreviations
            
            for w in replaceAbbreviations(p):
                addressTable[i].append(w.decode('ascii', 'ignore'))

    #Save as json to a file
    print "Saving json data"

    data = json.dumps(addressTable)
    with open("addressLookupTable.json", "w") as f:
        f.write(data)

'''
Loads all the addresses from the ppr file
return list of pairs (tr, m) 
    where:
        tr = The triple (date: address: price) as a string
        m = The modified address tokens
'''
def loadAddresses(filename):
    pprFile = open(filename, "r")

    addressList = []
    for l in pprFile:
        #Trim the leading and trailing quotes and then split by the remaining quotes
        tokens = l[1:-1].split("\"")
        if len(tokens) > 3:
            #address = nltk.wordpunct_tokenize(tokens[2])
    
            addressTokens = tokens[2].split(",")
            addressTokens = addressTokens[0:2] + [w for w in nltk.wordpunct_tokenize("".join(addressTokens[2:])) if w not in string.punctuation]
            
            m = [w.translate(string.maketrans("",""), string.punctuation).strip().lower() for w in addressTokens]
            #Put all the address components into lower case
            #m = [w.lower().strip() for w in address if w.strip() not in PUNCTUATION]
            #Every odd token is a comma, so skip them
            tr = ":".join([tokens[0], tokens[2], tokens[8]])
            addressList.append((tr, m))

    return addressList

def getPermutations(baseString, array):
    #Base case: Empty array yields base string
    if len(array) == 0:
        return [baseString]

    perms = []
    
    p = baseString
    for i in range(len(array)):
        p += " " + array[i]
        perms.append(p)

    #Get the permutations of the rest of the array
    return perms + getPermutations(baseString, array[1:])
    

ABBREVIATIONS = [(" co "," county "),
    (" co. "," county "),
    (" rd "," road "),
    (" rd. "," road "),
    (" st "," street "),
    (" st. "," street ")]

def replaceAbbreviations(address):
    #The original address unmodified
    results = [address]

    #Replace all abbreviations with their full text
    for abbrev in ABBREVIATIONS:
        newAddress = address.replace(abbrev[0], abbrev[1])
        if newAddress != address:
            results.append(newAddress)

        #Also replace all full words with their abbreviations
        newAddress = address.replace(abbrev[1], abbrev[0])
        if newAddress != address:
            results.append(newAddress)

    return results


if __name__ == "__main__":
    main()
