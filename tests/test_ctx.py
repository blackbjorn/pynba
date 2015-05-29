import unittest
from pynba.stacked import LOCAL_STACK
from pynba.wsgi import pynba
from pynba.wsgi import RequestContext


def reporter(arg, *args, **kwargs):
    return arg


class ContextTestCase(unittest.TestCase):
    def test_config(self):
        environ = {}
        ctx = RequestContext(reporter, environ)
        assert ctx.scriptname == ''

        ctx = RequestContext(reporter, environ, prefix="foo")
        assert ctx.scriptname.startswith('foo')

    def test_context(self):
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
        assert not pynba.enabled

        environ = {}
        with RequestContext(reporter, environ) as ctx:
            assert pynba.enabled
            timer = pynba.timer(foo='bar')
            assert timer in pynba.timers

        ctx.flush()
        with self.assertRaises((RuntimeError, AttributeError)):
            assert timer in pynba.timers

        with ctx:
            ctx.flush()
