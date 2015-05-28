try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pynba.globals import pynba
from pynba.local import LOCAL_STACK
from contextlib import contextmanager

class GlobalTestCase(unittest.TestCase):
    def test_context(self):
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
