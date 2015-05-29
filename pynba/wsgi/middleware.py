"""
    Pynba
    ~~~~~

    :copyright: (c) 2015 by Xavier Barbosa.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import, unicode_literals

from .ctx import RequestContext
from pynba.core import Reporter

__all__ = ['PynbaMiddleware']


class PynbaMiddleware(object):
    """Used to decorate main apps.

    Properties:
        app (callable): The main WSGI app that will be monitored.
        address (str): The address to the UDP server.
        config (dict): basically optional parameters
        reporter (Reporter): A custom reporter
        ctx_factory (RequestContext): A custom request_context
    """

    default_ctx = RequestContext
    default_reporter = Reporter

    def __init__(self, app, address, reporter=None, ctx_factory=None,
                 **config):
        self.app = app
        self.address = address
        self.reporter = reporter or self.default_reporter(address)
        self.ctx_factory = ctx_factory or self.default_ctx
        self.config = config

    def __call__(self, environ, start_response):
        with self.request_context(environ):
            return self.app(environ, start_response)

    def request_context(self, environ):
        """
        :param environ: The WSGI environ mapping.
        :return: will return a new instance of :class:`~.ctx.RequestContext`
        """
        return self.ctx_factory(self.reporter, environ, **self.config)
