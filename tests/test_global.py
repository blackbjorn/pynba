import unittest
from contextlib import contextmanager
from pynba.stacked import LOCAL_STACK, LocalProxy


class GlobalTestCase(unittest.TestCase):
    def test_context(self):
        pynba = LocalProxy(enabled=False)

        @pynba.timer(foo="bar")
        def foo():
            """docstring for foo"""
            pass

        with self.assertRaises(RuntimeError):
            foo()

        class X(object):
            @contextmanager
            def timer(self, *args, **kwargs):
                yield
        x = X()
        LOCAL_STACK.pynba = x

        foo()
