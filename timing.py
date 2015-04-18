from time import clock
import atexit

start = clock()


def exitlog():
    end = clock()
    diff = end - start

    secs = diff % 60
    mins = (diff / 60) % 60
    hours = (diff / (60 * 60)) % 60
    print "%d:%d:%d" % (hours, mins, secs)

atexit.register(exitlog)
