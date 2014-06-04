try:
    import unittest2 as unittest
except ImportError:
    import unittest

from iscool_e.pynba.ctx import RequestContext
from iscool_e.pynba.collector import DataCollector
from iscool_e.pynba.globals import pynba
from iscool_e.pynba.local import LOCAL_STACK

class ContextTestCase(unittest.TestCase):
    def test_config(self):
        reporter = lambda x: x
        environ = {}
        ctx = RequestContext(reporter, environ)
        assert ctx.scriptname == ''

        ctx = RequestContext(reporter, environ, prefix="foo")
        assert ctx.scriptname.startswith('foo')

    def test_context(self):
        reporter = lambda x: x
        environ = {}

        ctx = RequestContext(reporter, environ)
        top = LOCAL_STACK.pynba
        assert top is None
        assert ctx.pynba is None

        ctx.push()
        top = LOCAL_STACK.pynba
        assert ctx.pynba == top

        top = LOCAL_STACK.pynba
        ctx.pop()
        assert ctx.pynba is None
        assert ctx.pynba != top

    def test_context2(self):
        with self.assertRaises((RuntimeError, AttributeError)):
            pynba.enabled

        reporter = lambda *x, **y: x
        environ = {}
        with RequestContext(reporter, environ) as ctx:
            timer = pynba.timer(foo='bar')
            self.assertIn(timer, pynba.timers)

        ctx.flush()
        with self.assertRaises((RuntimeError, AttributeError)):
            self.assertIn(timer, pynba.timers)

        with ctx:
            ctx.flush()
