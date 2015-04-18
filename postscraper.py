from bs4 import BeautifulSoup
import json
import urlparse

import copy
import time
import datetime

import os, errno
import sys, inspect
import logging

#Import some modules in common folder
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"common")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)

from pagereader import openurl
from datamanager import ThreadEntry, PostEntry, insertThreadEntry, insertPostEntry, updatePostEntry, loadThreadPosts, postEntryExists, threadEntryExists
 

MAX_REQUESTS_PER_RUN = 5760 #5760 * 5 sec timeouts = 8 hours
DEFAULT_THREADS_PARAMS = {"f": 10, "start": 0}
DEFAULT_POSTS_PARAMS = {"f": 10, "t": 0, "start": 0}
DEFAULT_PROGRESS = {"get_params": copy.deepcopy(DEFAULT_THREADS_PARAMS), "offset": 0}


PROGRESS_FILENAME = "output/posts_progress.txt"
URL_THREADS = "http://www.thepropertypin.com/viewforum.php"
URL_POSTS = "http://www.thepropertypin.com/viewtopic.php"

numRequests = 0
progress = {}

def main():

    initLogging()

    #First load the current progress
    progress = loadProgress()
    logging.info("Loaded with progress %s", str(progress))

    isFinalThread = False

    #Next start the loop of requests
    isFinished = False
    while not isFinished:
        #Get all the threads on the current page
        threads, isFinalPage = getThreadEntries(progress["get_params"])
        print "Found %d threads" % len(threads)

        global numRequests
        numRequests = numRequests + 1

        print "Thread %d/%d" % (progress["get_params"]["start"] + progress["offset"], progress["get_params"]["start"] + len(threads))

        #Start at the offset; this is the thread we were at in the previous run
        while progress["offset"] < len(threads):
            t = progress["offset"]

            if not threadEntryExists(threads[t].thread_id):
                insertThreadEntry(threads[t])
            else:
                logging.info("Beginning scan of thread %s", threads[t].thread_id)

            #Retrieve the existing posts from the database
            posts_in_db = len(loadThreadPosts(threads[t].thread_id))

            # If the number of posts has changed (or the case where the thread has no replies - we assume we haven't looked at it yet)
            if (threads[t].numposts == 1 or posts_in_db < threads[t].numposts):
                #
                # Scrape this thread
                #
                retrieveAllPosts(threads[t].thread_id, posts_in_db)
            else:
                #
                # Gone past the final updated thread
                #
                pass

            progress["offset"] = progress["offset"] + 1

            #If the request limit was reached
            if (numRequests > MAX_REQUESTS_PER_RUN):
                isFinished = True
                break

        print "%s/%s requests" % (numRequests, MAX_REQUESTS_PER_RUN)

        # Reset progress if we've gone through all the threads on this page
        if progress["offset"] >= len(threads):
            logging.info("Going to next page of threads: start=%s", progress["get_params"]["start"])
            progress["offset"] = 0

        if not isFinished:
            if (isFinalPage):
                isFinished = True
                print "Gone past all updated threads at threads %s" % progress["get_params"]["start"] 
                progress = copy.deepcopy(DEFAULT_PROGRESS)
            else:
                isFinished = numRequests > MAX_REQUESTS_PER_RUN
                # Go to the next page
                progress["get_params"]["start"] = progress["get_params"]["start"] + 45

    logging.info("Finished, with %s/%s requests completed", numRequests, MAX_REQUESTS_PER_RUN)
    logging.info("Saving progress: %s", progress)
    saveProgress(progress)

def getThreadEntries(get_params):
    '''Send a http request to get the page contents'''
    page = openurl(URL_THREADS, get_params)

    global numRequests
    numRequests = numRequests + 1

    soup = BeautifulSoup(page)
    threadEntries = getLinksFromPage(soup)
    return threadEntries, isFinalPage(soup)

def getPostEntries(get_params):
    '''Send a http request to get the page contents'''
    page = openurl(URL_POSTS, get_params);

    soup = BeautifulSoup(page)
    postEntries = getPostsFromPage(soup, get_params["t"], get_params["start"])
    return postEntries, isFinalPage(soup)



def retrieveAllPosts(thread_id, startoffset):
'''
Returns True if all posts were retrieved
Returns False if gone past the final updated thread
thread_id = the thread to scrape posts from
startoffset = the offset in the thread from which to start scraping posts
'''
    get_params = copy.deepcopy(DEFAULT_POSTS_PARAMS)
    get_params["t"] = thread_id

    isFinished = False

    while not isFinished:
        postEntries, isFinalPage = getPostEntries(get_params)

        global numRequests
        numRequests = numRequests + 1
        
        #print get_params
        print "Inserting/Updating %d posts!" % len(postEntries)
        #Insert all the posts into the database
  
        postsAdded = 0
        for post in postEntries:
            if not postEntryExists(post.thread_id, post.post_id):
                postsAdded = postsAdded + 1
                insertPostEntry(post)

        if postsAdded > 0:
            logging.info("Added %d posts", postsAdded)
        if (isFinalPage):
            isFinished = True
        get_params["start"] = get_params["start"] + 15


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

    progress = {}
    if (os.path.exists(PROGRESS_FILENAME)): 
        with open(PROGRESS_FILENAME, 'r') as f:
            progress = json.loads(f.read())
    else:
        progress = copy.deepcopy(DEFAULT_PROGRESS)
        saveProgress(progress)
    return progress

def saveProgress(progress):
    with open(PROGRESS_FILENAME, 'w') as f:
        f.write(json.dumps(progress))


def getPostsFromPage(soup, thread_id, start):
    postAuthors = soup.find_all(class_ = "postauthor")
   
    i = 0

    posts = []
    for authortag in postAuthors:
        timestamp = getTimestampTag(authortag)

        content = str(authortag.find_next(class_ = "postbody")).decode("utf-8")
        author = authortag.string
        posts.append(PostEntry(author, content, timestamp, thread_id, start + i))
        i = i + 1

    return posts

def getTimestampTag(soup):
    postLink = soup.find_next("a")
    
    #Skip over the <a> and <b> tags
    result = postLink.next_sibling.next_sibling

    #Ignore the special character at the end and the space at the start
    result = result[1:-1]

    dateformat_propertypin = "%a %b %d, %Y %I:%M %p"
    dateformat_sql = "%Y-%m-%d %H:%M:%S"

    #Convert the string timestamp to an integer timestamp
    timestamp = time.mktime(datetime.datetime.strptime(result.encode("utf-8"), dateformat_propertypin).timetuple())
    #Convert this integer to a better datetime format
    result = datetime.datetime.fromtimestamp(timestamp).strftime(dateformat_sql)
    return result

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
        timestamp = extractTimestamp(link["title"])

        # Extract the thread id from the get parameters in the link
        parsed = urlparse.urlparse(link["href"])
        thread_id = urlparse.parse_qs(parsed.query)['t'][0]
        
        numposts = int(link.find_next(class_ = "topicdetails").string) + 1 # Number of Posts =  Replies + OP
        entry = ThreadEntry(timestamp, link.string, thread_id, numposts)
        threads.append(entry)
    
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
