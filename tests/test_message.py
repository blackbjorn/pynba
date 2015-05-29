import unittest
from pynba.core import dumps, cast


class ProtoTestCase(unittest.TestCase):
    def test_hostname(self):
        assert cast('\n\x0bexample.com') == dumps(hostname='example.com')

    def test_server_name(self):
        assert cast('\x12\nserver.lan') == dumps(server_name='server.lan')

    def test_script_name(self):
        assert cast('\x1a\x05/path') == dumps(script_name='/path')

    def test_request_count(self):
        assert cast(' \x01') == dumps(request_count=1)
        assert cast(' \x96\x01') == dumps(request_count=150)
        assert cast(' \xa7\x1f') == dumps(request_count=4007)
        assert cast(' \x87\x92\x8a\xf7\x0e') == dumps(request_count=4007823623)

    def test_request_time(self):
        assert cast(b'=\xf86M>') == dumps(request_time=0.200405)

    def test_dictionary(self):
        casted = cast('z\x03fooz\x03barz\x03baz')
        assert casted == dumps(dictionary=['foo', 'bar', 'baz'])

    def test_timer_hit_count(self):
        assert cast('P*P\xe8\x07P\x02') == dumps(timer_hit_count=[42, 1000, 2])

    def test_timer_value(self):
        casted = cast(b']ff(B]\xcd\xcc\xcc=]ff\x06@')
        assert casted == dumps(timer_value=[42.1, .1000, 2.1])

    def test_mix_1(self):
        casted = cast('\n\x0bexample.com \x17z\x03fooz\x03barz\x03baz')
        assert casted == dumps(hostname='example.com',
                               request_count=23,
                               dictionary=['foo', 'bar', 'baz'])
