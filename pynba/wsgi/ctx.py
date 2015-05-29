"""
    Pynba
    ~~~~~

    :copyright: (c) 2015 by Xavier Barbosa.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import, unicode_literals

import resource
from pynba.core import DataCollector
from pynba.stacked import LOCAL_STACK

__all__ = ['RequestContext']


class RequestContext(object):
    """
    A new instance will be created every new request.

    :param reporter: a :class:`Reporter` instance
    :param environ: the current WSGI environ mapping
    :param config: may have these keys:
                   ``prefix`` will prepend scriptname
    """

    def __init__(self, reporter, environ, **config):
        self.reporter = reporter

        #: config['prefix'] prepends the sent scriptname to pinba.
        #: config['tags'] prepends tags to pinba.
        self.config = config

        #: futur :class:`DataCollector`
        self.pynba = None
        #: will keep a snap of :func:`resource.getrusage`
        self.resources = None

        self._hostname = environ.get('SERVER_NAME', None)
        self._schema = environ.get('wsgi.url_scheme', None)
        self._scriptname = environ.get('PATH_INFO', '')
        self._servername = ''

    @property
    def scriptname(self):
        out = self.config.get('prefix', '')

        if self.pynba:
            pynba = self.pynba
            if pynba.scriptname:
                return out + self.pynba.scriptname
        return out + self._scriptname

    @property
    def hostname(self):
        if self.pynba:
            pynba = self.pynba
            if pynba.hostname:
                return pynba.hostname
        if self._hostname:
            return self._hostname

        return None

    @property
    def servername(self):
        return self._servername

    @property
    def tags(self):
        if self.pynba:
            pynba = self.pynba
            response = pynba.tags or {}
        else:
            response = self.config.get('tags', {})
        return response

    def push(self):
        """Pushes current context into local stack.
        """

        self.pynba = DataCollector(self._scriptname,
                                   self._hostname,
                                   self._schema,
                                   self.config.get('tags', {}))
        self.pynba.start()
        LOCAL_STACK.pynba = self.pynba
        self.resources = resource.getrusage(resource.RUSAGE_SELF)

    def pop(self):
        """Pops current context from local stack.
        """

        del LOCAL_STACK.pynba
        self.pynba = None
        self.resources = None

    def __enter__(self):
        """Opens current scope.
        """

        self.push()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Closes current scope.
        """

        self.flush()
        self.pop()

    def flush(self):
        """Flushes timers.

        Similar to the PHP ``pinba_flush()`` function.
        scriptname sent to pinba will be prepend by config['prefix']
        """

        if not self.pynba or not self.pynba.enabled:
            return

        self.pynba.stop()
        timers = [timer for timer in self.pynba.timers if timer.elapsed]
        document_size = self.pynba.document_size
        memory_peak = self.pynba.memory_peak
        usage = resource.getrusage(resource.RUSAGE_SELF)
        ru_utime = usage.ru_utime - self.resources.ru_utime
        ru_stime = usage.ru_stime - self.resources.ru_stime
        memory_footprint = self.pynba.memory_peak
        schema = self.pynba.schema

        self.reporter(
            self.servername,
            self.hostname,
            self.scriptname,
            self.pynba.elapsed,
            timers,
            ru_utime=ru_utime,
            ru_stime=ru_stime,
            document_size=document_size,
            memory_peak=memory_peak,
            memory_footprint=memory_footprint,
            schema=schema,
            tags=self.tags
        )

        self.pynba.flush()
