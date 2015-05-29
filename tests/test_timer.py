import unittest
from pynba.core import Timer


class TimerTestCase(unittest.TestCase):
    def test_timer(self):
        def runner(timer):
            assert timer.started is False
            assert timer.elapsed is None

            with self.assertRaises(RuntimeError):
                timer.stop()

            timer.start()
            assert timer.elapsed is None
            assert timer.started is True
            with self.assertRaises(RuntimeError):
                timer.start()

            timer.stop()
            assert timer.started is False
            assert isinstance(timer.elapsed, float)

            assert timer.tags == {'foo': 'bar'}

        timer = Timer({"foo": "bar"})

        runner(timer)

        cloned = timer.clone()
        assert timer is not cloned

        runner(cloned)

    def test_timer_context(self):
        timer = Timer({"foo": "bar"})
        assert timer.started is False
        with timer as t:
            assert timer is t
            assert t.started is True

        assert timer is t
        assert t.started is False

    def test_timer_decorator(self):
        def runner():
            return

        timer = Timer({"foo": "bar"})
        decorated = timer(runner)
        decorated()

    def test_timer_repr(self):
        timer = Timer({"foo": "bar"})
        assert 'Timer' in repr(timer)
        timer.start()
        assert 'started:' in repr(timer)
        timer.stop()
        assert 'elapsed:' in repr(timer)
