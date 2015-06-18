"""
    Pynba
    ~~~~~

    :copyright: (c) 2015 by Xavier Barbosa.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import, unicode_literals

import resource
import socket
import sys
from pynba.core import DataCollector, Reporter

__all__ = ['ScriptMonitor']


class ScriptMonitor(object):
    """Helper for monitoring standalone scripts.

    >>> monitor = ScriptMonitor(('127.0.0.1', 30002))
    >>> timer = monitor.timer(tag1='bar')
    >>> timer.start()
    >>> timer.stop()
    >>>
    >>> @monitor.timer(tag1='bar')
    >>> def baz():
    >>>     pass
    >>> baz()
    >>>
    >>> with monitor.timer(tag1='baz'):
    >>>     print "hello"
    >>>
    >>> monitor.send()
    """

    default_reporter = Reporter

    def __init__(self, address, hostname=None, scriptname=None,
                 servername=None, reporter=None, tags=None, autostart=True):
        self.reporter = reporter or self.default_reporter(address)
        self.collector = DataCollector(tags=tags or {})
        self.hostname = hostname or socket.gethostname()
        self.scriptname = scriptname or " ".join(sys.argv)
        self.servername = servername or socket.gethostname()
        self.resources = None
        self.ru_utime = None
        self.ru_stime = None

        if autostart:
            self.start()

    @property
    def started(self):
        return self.collector.started

    @property
    def elapsed(self):
        return self.collector.elapsed

    def start(self):
        """Starts monitoring.
        """
        self.collector.start()
        self.resources = resource.getrusage(resource.RUSAGE_SELF)
        return self

    def stop(self):
        """Stops current elapsed time and every attached timers.
        """
        self.collector.stop()
        usage = resource.getrusage(resource.RUSAGE_SELF)
        self.ru_utime = usage.ru_utime - self.resources.ru_utime
        self.ru_stime = usage.ru_stime - self.resources.ru_stime
        return self

    @property
    def tags(self):
        """Returns collector tags.
        """
        return self.collector.tags

    def timer(self, **kwargs):
        """Factory new timer.
        """
        return self.collector.timer(**kwargs)

    def flush(self):
        """Flushes timers.
        """
        self.collector.flush()
        return self

    def send(self):
        """Sends timers to server.
        """
        self.stop()
        timers = [timer for timer in self.collector.timers if timer.elapsed]
        document_size = self.collector.document_size
        memory_peak = self.collector.memory_peak
        ru_utime = self.ru_utime
        ru_stime = self.ru_stime

        self.reporter(
            self.servername,
            self.hostname,
            self.scriptname,
            self.collector.elapsed,
            timers,
            ru_utime=ru_utime,
            ru_stime=ru_stime,
            document_size=document_size,
            memory_peak=memory_peak,
            status=None,
            memory_footprint=None,
            schema=None,
            tags=self.collector.tags
        )

        self.flush()
