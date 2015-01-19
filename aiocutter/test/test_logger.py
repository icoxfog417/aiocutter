import unittest
import logging
import sys
from aiocutter import logger


class TestLogger(unittest.TestCase):

    def test_logging(self):
        handler = logging.StreamHandler(sys.stderr)
        test_logger = logger.create_logger("test_logger", logging.WARNING, handler=handler)
        test_logger.warning("Warning Message")
