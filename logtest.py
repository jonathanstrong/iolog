import logging
import logging.handlers
import time

logger = logging.getLogger(__name__)
handler = logging.handlers.SocketHandler('localhost', 9033)
stream = logging.StreamHandler()
logger.addHandler(handler)
logger.addHandler(stream)
while True: 
    logger.warning('ping')
    time.sleep(.001)
