try:
    import unittest2 as unittest
except ImportError:
    import unittest

from iscool_e.pynba.util import ScriptMonitor
from multiprocessing import Process
from time import sleep

class ScriptMonitorCase(unittest.TestCase):
    def test_main(self):
        def reporter(*args, **kwargs):
            pass
        monitor = ScriptMonitor(('127.0.0.1', 3002), reporter=reporter)

        assert len(monitor.collector.timers) == 0

        timer = monitor.timer(tag1="foo")
        assert len(monitor.collector.timers) == 1

        monitor.flush()
        assert len(monitor.collector.timers) == 0

        assert monitor.ru_utime is None
        assert monitor.ru_stime is None

        monitor.send()

        assert monitor.ru_utime is not None
        assert monitor.ru_stime is not None
