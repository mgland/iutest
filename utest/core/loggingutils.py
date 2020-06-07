import logging

logger = logging.getLogger(__name__)

def allLoggingLevel():
    return (
            logging.NOTSET, 
            logging.DEBUG, 
            logging.INFO, 
            logging.WARNING, 
            logging.ERROR, 
            logging.FATAL, 
    )
    

def loggingLevels(*dotPaths):
    return [logging.getLogger(dotPath).level for dotPath in dotPaths]


def setLoggingLevel(level, *dotPaths):
    levelName = logging.getLevelName(level)
    for dotPath in dotPaths:
        logging.getLogger(dotPath).setLevel(level)
        logging.info("Set logging level of %s to: %s", dotPath, levelName)
