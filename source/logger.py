import logging
import sys

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

logger.addHandler(logging.FileHandler("app.log"))
logger.addHandler(logging.StreamHandler(sys.stdout))

if __name__ == "__main__":
    logger.debug("testing log.")
