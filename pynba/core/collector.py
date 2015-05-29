"""
    Pynba
    ~~~~~

    :copyright: (c) 2015 by Xavier Barbosa.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import, unicode_literals

import functools
import os
import time
from .log import logger
from enum import Enum

__all__ = ['DataCollector', 'Timer']

# time.clock() has better accuracy in windows
now = time.clock if os.name == 'nt' else time.time


class RunningState(Enum):
    initialized = 0
    started = 1
    stoped = 2


class Timed:

    def __init__(self):
        self._state = RunningState.initialized

    @property
    def started(self):
        """Tell if timer is started
        """
        return self._state == RunningState.started

    @property
    def elapsed(self):
        """Returns the elapsed time in seconds
        """
        if self._state == RunningState.stoped:
            return self._tt_elapsed

    @property
    def dt_start(self):
        """Returns the elapsed time in seconds
        """
        if self._state != RunningState.initialized:
            return self._tt_start
        return None

    def _start(self):
        """Starts timer
        """
        if self._state == RunningState.started:
            raise RuntimeError('Already started')
        self._state = RunningState.started
        self._tt_start = now()

    def _stop(self):
        """Stops timer
        """
        if self._state != RunningState.started:
            raise RuntimeError('Not started')
        self._tt_end = now()
        self._tt_elapsed = self._tt_end - self._tt_start
        self._state = RunningState.stoped

    def _flush(self):
        """Flushs.
        """
        self._state = RunningState.started
        self._tt_start = now()


class Timer(Timed):
    """
    Properties:
        tags (dict): tags for the current timer
        parent (DataCollector): attached data collector
        data (dict): attached data

    Differences with the PHP version

    =========================== =================================
    PHP                         Python
    =========================== =================================
    pinba_timer_data_merge()    not applicabled use instance.data
    pinba_timer_data_replace()  not applicabled use instance.data
    pinba_timer_get_info()      not implemented
    =========================== =================================

    """

    def __init__(self, tags, parent=None):
        """
        Tags values can be any scalar, mapping, sequence or callable.
        In case of a callable, rendered value must be a sequence.

        Parameters:
            tags (dict): each values can be any scalar, mapping, sequence or
                         callable. In case of a callable, rendered value must
                         be a sequence.
            parent (DataCollector): attached data collector
        """
        Timed.__init__(self)
        self.tags = dict(tags)
        self.parent = parent
        self.data = None

    def delete(self):
        """Discards timer from parent
        """
        if self.parent:
            self.parent.timers.discard(self)

    def clone(self):
        """Clones timer
        """
        instance = Timer(self.tags, self.parent)
        if self.data:
            instance.data = self.data

        if self.parent:
            self.parent.timers.add(instance)
        return instance

    def start(self):
        """Starts timer
        """
        self._start()
        return self

    def stop(self):
        """Stops timer
        """
        self._stop()
        return self

    def __enter__(self):
        """Acts as a context manager.

        Automatically starts timer.
        Example::

            with pynba.timer(foo=bar) as timer:
                # LOC to be timed
                pass
        """
        if not self.started:
            self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Closes context manager.

        Automatically stops timer
        """
        if self.started:
            self.stop()

    def __call__(self, func):
        """Acts as a decorator.

        Automatically starts and stops timer's clone.
        Example::

            @pynba.timer(foo=bar)
            def function_to_be_timed():
                pass
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self.clone():
                response = func(*args, **kwargs)
            return response
        return wrapper

    def __repr__(self):
        if self._state == RunningState.stoped:
            label = ' elapsed:'
            period = self.elapsed
        elif self._state == RunningState.started:
            label = ' started:'
            period = self.dt_start
        else:
            label = ''
            period = 0

        return '<{0}({1}){2}{3}>'.format(
            self.__class__.__name__,
            self.tags,
            label, period)


class DataCollector(Timed):
    """
    This is the main data container.

    :param scriptname: the current scriptname
    :param hostname: the current hostname
    :param schema: the current schema
    :param tags: tags for the current script

    Differences with the PHP version

    =========================== =========================
    PHP                         Python
    =========================== =========================
    pinba_get_info()            not applicabled while the current
                                instance data are already exposed.
    pinba_script_name_set()     self.scriptname
    pinba_hostname_set()        not implemented, use hostname
    pinba_timers_stop()         self.stop()
    pinba_timer_start()         self.timer
    =========================== =========================

    """

    def __init__(self, scriptname=None, hostname=None, schema=None, tags=None):
        Timed.__init__(self)
        self.enabled = True
        self.timers = set()
        self.scriptname = scriptname
        self.hostname = hostname
        self.schema = schema
        self.tags = dict(tags or {})

        #: You can use this placeholder to store the real document size
        self.document_size = None
        #: You can use this placeholder to store the memory peak
        self.memory_peak = None
        #: You can use this placeholder to store the memory footprint
        self.memory_footprint = None

    def start(self):
        """Starts"""
        self._start()
        return self

    def stop(self):
        """Stops current elapsed time and every attached timers.
        """
        self._stop()
        for timer in self.timers:
            if timer.started:
                timer.stop()
        return self

    def timer(self, **tags):
        """Factory new timer.
        """
        timer = Timer(tags, self)
        self.timers.add(timer)
        return timer

    def flush(self):
        """Flushs.
        """
        logger.debug('flush', extra={
            'timers': self.timers,
            'elapsed': self.elapsed,
        })
        self._flush()
        self.timers.clear()
        return self
