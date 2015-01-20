import unittest
import logging
import sys
from aiocutter import logger


class TestLogger(unittest.TestCase):

    def test_log_msg(self):
        handler = logging.StreamHandler(sys.stderr)
        test_logger = logger.create_logger("test_logger", logging.WARNING, handler=handler)
        test_logger.warning("Warning Message")

    def test_log_exception(self):
        handler = logging.StreamHandler(sys.stderr)
        test_logger = logger.create_logger("test_logger", logging.WARNING, handler=handler)
        try:
            raise Exception("exception caused")
        except Exception as ex:
            test_logger.exception("exception occurred")
