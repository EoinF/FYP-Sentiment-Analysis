import os
import requests
import errno
import time

def openurl_cached(url, get_params):
    page = ""

    try:
        os.makedirs("cache")
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    cache_filename = "cache/" + str(get_params["f"]) + "_" + str(get_params["start"])

    if ("t" in get_params):
        cache_filename = cache_filename + "_" + str(get_params["t"])

    cache_filename = cache_filename + ".txt"

    if (os.path.exists(cache_filename)):
        print "Cache found. Reading from file: " + cache_filename
        with open(cache_filename, 'r') as f:
            page = f.read()
    else:
        print "No cache found. Http request: " + url + str(get_params)
        time.sleep(5)
        page = requests.get(url, params=get_params).text
        with open(cache_filename, 'w') as f:
            f.write(page.encode("utf-8"))

    return page

def openurl(url, get_params):
    page = requests.get(url, params=get_params).text

    time.sleep(5)

    return page
