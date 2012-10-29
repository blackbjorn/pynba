# -*- coding: utf-8 -*-
"""
    IsCool-e Pynba
    ~~~~~~~~~~~~~~

    :copyright: (c) 2012 by IsCool Entertainment.
    :license: MIT, see LICENSE for more details.
"""

import resource
import socket
import sys
from .reporter import Reporter
from .collector import DataCollector

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

    def __init__(self, address, hostname=None, scriptname=None, servername=None, reporter=None):
        self.reporter = reporter if reporter else self.default_reporter(address)
        self.collector = DataCollector()
        self.hostname = hostname if hostname else socket.gethostname()
        self.scriptname = scriptname if scriptname else " ".join(sys.argv)
        self.servername = servername if servername else socket.gethostname()
        self.resources = None
        self.ru_utime = None
        self.ru_stime = None
        self.start()

    def start(self):
        """Starts"""
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
            servername= self.servername,
            hostname= self.hostname,
            scriptname= self.scriptname,
            elapsed= self.collector.elapsed,
            timers= timers,
            ru_utime= ru_utime,
            ru_stime= ru_stime,
            document_size= document_size,
            memory_peak= memory_peak
        )

        self.flush()
