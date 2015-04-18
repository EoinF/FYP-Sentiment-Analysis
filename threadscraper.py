from bs4 import BeautifulSoup
import json
import urlparse

import time
import datetime

import os, errno
import sys, inspect
import logging

#Modules in common folder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"common")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

from pagereader import openurl
from datamanager import ThreadEntry, insertThreadEntry

MAX_REQUESTS_PER_RUN = 300
DEFAULT_PARAMS = {"f": 10, "start": 0}

PROGRESS_FILENAME = "output/threads_progress.txt"
URL = "http://www.thepropertypin.com/viewforum.php"

def main():
    get_params = loadProgress()

    numRequests = 0
    threadEntries = []
    isFinished = False
    
    initLogging()
    while not isFinished:
        page = openurl(URL, get_params)

        soup = BeautifulSoup(page)
        #Add to the list of links
        threadEntries = getLinksFromPage(soup)

        for entry in threadEntries:
            insertThreadEntry(entry)
        
        numRequests = numRequests + 1

        if (isFinalPage(soup)):
            isFinished = True
            get_params = DEFAULT_PARAMS #Restore the params to default
        else:
            isFinished = numRequests > MAX_REQUESTS_PER_RUN
            #Go to the next page
            get_params["start"] = get_params["start"] + 45

    saveProgress(get_params)

def initLogging(): 
    try:
        os.makedirs("logs")
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    # Setup logging to a file with timestamps
    logging.basicConfig(filename='logs/scraper.log', format='%(asctime)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.DEBUG)

def loadProgress():
    try:
        os.makedirs("output")
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    progress = []
    if (os.path.exists(PROGRESS_FILENAME)): 
        with open(PROGRESS_FILENAME, 'r') as f:
            progress = json.loads(f.read())
    else:
        progress = DEFAULT_PARAMS
        saveProgress(progress)
    return progress

def saveProgress(progress):
    with open(PROGRESS_FILENAME, 'w') as f:
        f.write(json.dumps(progress))

def getLinksFromPage(soup):
    topicsrow = getTopicsRow(soup)

    # Get all the links from the following rows in the table
    rows = topicsrow.find_next_siblings("tr")

    # Discard the last row - it's only a separator row
    rows = rows[:-1]

    # Get a list of all the "a" html tags within each row
    links = [tr("a")[0] for tr in rows]

    #f_match = lambda tag: tag.name == "a" and tag.has_attr('title')
    #links = topicsrow.find_all_next(f_match)

    threads = []
    # Create an array of thread entries
    for link in links:
        timestamp = str(extractTimestamp(link["title"]))

        # Extract the thread id from the get parameters in the link
        parsed = urlparse.urlparse(link["href"])
        thread_id = urlparse.parse_qs(parsed.query)['t'][0]

        threads.append(ThreadEntry(timestamp, link.string, thread_id, 0))

    return threads

def getTopicsRow(soup):
    pagecontent = soup.find(id="pagecontent")
    #Navigate to the "tr" tag that contains the text Topics
    topicsrow = pagecontent(text="Topics")[0].parent.parent.parent
    return topicsrow

def isFinalPage(soup):
    pagecontent = soup.find(id="pagecontent")
    #Navigate to the first tag that has the "nav" class
    navtag = pagecontent.find(class_="nav")

    pageNums = navtag("strong")
    return pageNums[0].string == pageNums[1].string

def extractTimestamp(text):
    #Ignore the "Posted: " part of the text
    result = text[8:]

    dateformat_propertypin = "%a %b %d, %Y %I:%M %p"
    dateformat_sql = "%Y-%m-%d %H:%M:%S"

    #Convert the string timestamp to an integer timestamp
    timestamp = time.mktime(datetime.datetime.strptime(result, dateformat_propertypin).timetuple())
    #Convert this integer to a better datetime format
    result = datetime.datetime.fromtimestamp(timestamp).strftime(dateformat_sql)
    return result


if __name__ == "__main__":
	main()
