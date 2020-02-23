import logging
import sys
import matplotlib.pyplot as plt


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    if not logger.hasHandlers():
        print("Adding handler to logger\n")
        log_handler = logging.StreamHandler(sys.stdout)
        log_handler.setLevel(logging.DEBUG)
        logger.addHandler(log_handler)
    
    
    logger.debug("don't worry 'bout it")
    logger.info("Hey what up. Here's some info.")
    logger.warning("Warning WATCH OUT!")
    logger.error("Error will robinson")
    logger.critical("Super important critical")
    
    # put this in here just to be sure matplotlib logger is not triggered
    plt.scatter(1,1)