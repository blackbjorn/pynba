# -*- coding: utf-8 -*-
"""
    Pynba
    ~~~~~

    :copyright: (c) 2015 by Xavier Barbosa.
    :license: MIT, see LICENSE for more details.
"""

from .reporter import Reporter
from .ctx import RequestContext

cdef class PynbaMiddleware(object):
    """Used to decorate main apps.

    :param app: The main WSGI app that will be monitored.
    :param address: The address to the UDP server.
    :param config: basically optional parameters
    """

    cdef object _default_ctx
    cdef public object app
    cdef public object reporter
    cdef public object config

    property default_ctx:
        def __get__(self):
            if self._default_ctx:
                return self._default_ctx
            return RequestContext

        def __set__(self, ctx):
            self._default_ctx = ctx

        def __del__(self):
            self._default_ctx = None

    def __init__(self, object app, object address, **config):
        self.app = app
        self.reporter = Reporter(address)
        self.config = config

    def __call__(self, object environ, object start_response):
        with self.request_context(environ):
            return self.app(environ, start_response)

    def request_context(self, object environ):
        """
        :param environ: The WSGI environ mapping.
        :return: will return a new instance of :class:`~.ctx.RequestContext`
        """
        return self.default_ctx(self.reporter, environ, **self.config)

# PynbaMiddleware.default_ctx = RequestContext
