from collections import namedtuple
import MySQLdb
import logging
import os, errno
import getpass

''' 
** IMPORTANT **

 No care has been taken in this script to prevent sql injections.
 Avoid using this script when the user could potentially have malicious intentions

'''

dbtable = "u_eoinf"
dbusername = "eoinf"
dbaddress="userdb.netsoc.tcd.ie"

# Define the database table tuples
ThreadEntry = namedtuple("ThreadEntry", "timestamp title thread_id numposts")
PostEntry = namedtuple("PostEntry", "user content timestamp thread_id post_id")

# Initiate database connection
try:
    dbpassword = getpass.getpass("Please enter your password for database user %s@%s:" % (dbusername, dbaddress))
    db = MySQLdb.connect(dbaddress, dbusername, dbpassword, dbtable)
except MySQLdb.DatabaseError:
    logging.critical("Failed to connect to database")
    exit()

def main():
    '''This is simply a test script'''
    try:
        os.makedirs("../logs")
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    # Set up logging
    logging.basicConfig(filename='../logs/db.log', format='%(asctime)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.DEBUG)

    test_thread = ThreadEntry("2014-12-22 19:30:00", "Testing title", 1234567, 1)
    insertThreadEntry(test_thread)

    test_post = PostEntry("Eoin", "<p>Content</p>", "2014-12-23 00:30:00", 1234567, 1)
    insertPostEntry(test_post)
    closeConnection()


def insertThreadEntry(entry):
    assert type(entry) is ThreadEntry, "entry is not a ThreadEntry type"

    #Prepare an sql cursor object
    cursor = db.cursor()

    #Prepare the sql statement
    sql = "INSERT INTO Threads VALUES(%s, %s, %s)"
    args = entry.timestamp.encode('utf-8'), entry.title.encode('utf-8'), entry.thread_id.encode('utf-8')

    #logging.info("INSERT INTO Threads VALUES('%s', '%s', %s)", *args)

    try:
        #Execute the query
        cursor.execute(sql, args)
        db.commit()
    except MySQLdb.IntegrityError:
        logging.warn("Failed to insert values ('%s', '%s', %s) into Threads", *args)
    finally:
        cursor.close()

def insertPostEntry(entry):
    assert type(entry) is PostEntry, "entry is not a PostEntry type"

    #Prepare an sql cursor object
    cursor = db.cursor()

    #Prepare the sql statement
    sql = "INSERT INTO Posts VALUES(%s, %s, %s, %s, %s)"
    args = entry.user.encode('utf-8'), entry.content.encode('utf-8'), entry.timestamp.encode('utf-8'), entry.thread_id, entry.post_id

    try:
        #Execute the query
        cursor.execute(sql, args)
        db.commit()
    except MySQLdb.IntegrityError:
        logging.warn("Failed to insert values ('%s', '%s', '%s', %s, %s) into Posts", *args)
    finally:
        cursor.close()


def updatePostEntry(entry, newContent):
    #Prepare an sql cursor object
    cursor = db.cursor()

    #Prepare the sql statement
    sql = "UPDATE Posts SET content=%s WHERE thread_id = %s AND post_id = %s"
    args = newContent, entry.thread_id, entry.post_id
    
    #Execute the query
    cursor.execute(sql, args)

def loadThreadPosts(thread_id):

    #Prepare an sql cursor object
    cursor = db.cursor()

    #Prepare the sql statement
    sql = "SELECT * FROM Posts WHERE thread_id = %s"
    args = thread_id

    
    #Execute the query
    cursor.execute(sql, args)
    postEntries = []
    results = cursor.fetchall()
    for row in results:
        postEntries.append(PostEntry(*row))

    return postEntries

def loadAllThreads():    
    #Prepare an sql cursor object
    cursor = db.cursor()

    #Select all the thread objects
    cursor.execute("SELECT * FROM Threads")
    
    results = cursor.fetchall()

    threadEntries = []
    for row in results:
        threadEntries.append(ThreadEntry(*row, numposts=0))
        
    return threadEntries

def loadAllFirstPosts():
    #Prepare an sql cursor object
    cursor = db.cursor()

    #Select all the thread objects including their first post
    cursor.execute("""SELECT * FROM Threads 
        INNER JOIN Posts
        ON Posts.thread_id=Threads.thread_id
            WHERE Posts.post_id = 0""")
    
    results = cursor.fetchall()

    #Create an array of (thread, post) pairs
    firstposts = []
    for row in results:
        thread = ThreadEntry(*(row[0:3]), numposts=0)
        post = PostEntry(*(row[3:8]))
        firstposts.append((thread, post))
        
    return firstposts

def loadFromTimeRange(date_start, date_end):
    #Prepare an sql cursor object
    cursor = db.cursor()

    #Select all the thread objects including their posts
    sql = """SELECT * FROM Threads 
        INNER JOIN Posts
        ON Posts.thread_id=Threads.thread_id
        WHERE Threads.timestamp > %s AND Threads.timestamp < %s"""
    args = date_start, date_end

    cursor.execute(sql, args)

    results = cursor.fetchall()

    #Create an array of (thread, post) pairs
    firstposts = []
    for row in results:
        thread = ThreadEntry(*(row[0:3]), numposts=0)
        post = PostEntry(*(row[3:8]))
        firstposts.append((thread, post))
        
    return firstposts
    

def postEntryExists(thread_id, post_id): 
    #Prepare an sql cursor object
    cursor = db.cursor()

    #Prepare the sql statement
    sql = "SELECT * FROM Posts WHERE thread_id = %s AND post_id = %s"
    args = thread_id, post_id
    
    #Execute the query
    result = cursor.execute(sql, args)

    return result == 1

def threadEntryExists(thread_id): 
    #Prepare an sql cursor object
    cursor = db.cursor()

    #Prepare the sql statement
    sql = "SELECT * FROM Posts WHERE thread_id = %s"
    args = thread_id
    
    #Execute the query
    result = cursor.execute(sql, args)

    return result == 1

def closeConnection():
    db.close()


if __name__ == "__main__":
    main()
