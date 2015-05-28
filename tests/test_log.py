try:
    import unittest2 as unittest
except ImportError:
    import unittest

import logging
from collections import defaultdict

from pynba.log import logger
from pynba.collector import DataCollector
from pynba.reporter import Reporter

class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs.
    <http://stackoverflow.com/a/1049375>
    <http://www.domenkozar.com/category/mock/>
    """

    def __init__(self, *args, **kwargs):
        self.messages = defaultdict(list)
        logging.Handler.__init__(self, *args, **kwargs)

    def emit(self, record):
        self.messages[record.levelname.lower()].append(record.getMessage())
        # raise Exception(dict(self.messages))

    def reset(self):
        self.messages.clear()


class LogTestCase(unittest.TestCase):
    handler = MockLoggingHandler(level=logging.DEBUG)
    level = None

    def setUp(self):
        self.level = logger.getEffectiveLevel()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(self.handler)

    def tearDown(self):
        logger.setLevel(self.level)
        logger.removeHandler(self.handler)
        self.handler.reset()

    def test_simple(self):
        logger.debug('foo')
        logger.info('bar')
        logger.warning('baz')
        logger.error('qux')
        logger.critical('trololo')

        assert self.handler.messages == {
            'debug': ['foo'], 
            'info': ['bar'], 
            'warning': ['baz'], 
            'critical': ['trololo'], 
            'error': ['qux']
            }

    def test_collector(self):
        DataCollector().flush()
        assert self.handler.messages == {
            'debug': ['flush']
        }

    def test_reporter(self):
        Reporter.prepare('servername', 'hostname', 'scriptname', 0.0, [])
        assert self.handler.messages == {
            'debug': ['prepare protobuff']
        }
