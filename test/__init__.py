import os
import sys
import logging


sys.path.append(os.path.dirname(__file__))


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(name)s [%(levelname)s] %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
