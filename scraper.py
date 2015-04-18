import os, errno, logging

def main():

    try:
        os.makedirs("logs")
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    # Set up logging
    logging.basicConfig(filename='logs/scraper.log', format='%(asctime)s: %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', level=logging.DEBUG)

if __name__ == "__main__":
    main()
