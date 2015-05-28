try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pynba.collector import DataCollector

class CollectorTestCase(unittest.TestCase):
    def test_data_collector(self):
        scriptname = "foo"
        hostname = "bar"
        schema = "http"
        tags = {"baz": "qux"}
        collector = DataCollector(scriptname, hostname, schema, tags)
        self.assertTrue(collector.enabled)
        self.assertEqual(collector.timers, set())
        self.assertEqual(collector.scriptname, scriptname)
        self.assertEqual(collector.hostname, hostname)
        self.assertEqual(collector.schema, schema)
        self.assertEqual(collector.tags, tags)
        self.assertEqual(collector.dt_start, None)
        self.assertFalse(collector.started)
        self.assertEqual(collector.elapsed, None)
        with self.assertRaises(RuntimeError):
            collector.stop()

        collector.start()
        self.assertTrue(collector.started)
        self.assertEqual(collector.elapsed, None)
        with self.assertRaises(RuntimeError):
            collector.start()
        collector.stop()
        self.assertNotEqual(collector.elapsed, None)

    def test_linked_timer(self):
        collector = DataCollector()
        timer = collector.timer(foo='bar')

        self.assertIn(timer, collector.timers)
        cloned = timer.clone()
        self.assertIn(cloned, collector.timers)

        timer.delete()
        self.assertNotIn(timer, collector.timers)
        self.assertIn(cloned, collector.timers)

        cloned.delete()
        self.assertNotIn(cloned, collector.timers)


        timer2 = collector.timer(foo='bar')
        self.assertIn(timer2, collector.timers)
        collector.flush()
        self.assertNotIn(timer2, collector.timers)
