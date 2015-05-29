import unittest
from pynba.core import DataCollector


class CollectorTestCase(unittest.TestCase):
    def test_data_collector(self):
        scriptname = "foo"
        hostname = "bar"
        schema = "http"
        tags = {"baz": "qux"}
        collector = DataCollector(scriptname, hostname, schema, tags)
        assert collector.enabled is True
        assert collector.timers == set()
        assert collector.scriptname == scriptname
        assert collector.hostname == hostname
        assert collector.schema == schema
        assert collector.tags == tags
        assert collector.dt_start is None
        assert collector.started is False
        assert collector.elapsed is None
        with self.assertRaises(RuntimeError):
            collector.stop()

        collector.start()
        assert collector.started is True
        assert collector.elapsed is None
        with self.assertRaises(RuntimeError):
            collector.start()
        collector.stop()
        assert collector.elapsed is not None

    def test_linked_timer(self):
        collector = DataCollector()
        timer = collector.timer(foo='bar')

        assert timer in collector.timers
        cloned = timer.clone()
        assert cloned in collector.timers

        timer.delete()
        assert timer not in collector.timers
        assert cloned in collector.timers

        cloned.delete()
        assert cloned not in collector.timers

        timer2 = collector.timer(foo='bar')
        assert timer2 in collector.timers
        collector.flush()
        assert timer2 not in collector.timers
