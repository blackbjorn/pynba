# -*- coding: utf-8 -*-
"""
    IsCool-e Pynba
    ~~~~~~~~~~~~~~

    :copyright: (c) 2012 by IsCool Entertainment.
    :license: MIT, see LICENSE for more details.
"""

import functools
from .log import logger

cdef extern from "sys/time.h":
    ctypedef long time_t
    struct timeval:
        time_t tv_sec
        time_t tv_usec
    struct timezone:
        pass
    int gettimeofday(timeval *tv, timezone *tz)

cdef enum RunningState:
    initialized = 0,
    running = 1,
    finished = 2

cdef class Timer(object):
    """
    Differences with the PHP version

    =========================== =========================
    PHP                         Python
    =========================== =========================
    pinba_timer_data_merge()    not applicabled use instance.data
    pinba_timer_data_replace()  not applicabled use instance.data
    pinba_timer_get_info()      not implemented
    =========================== =========================

    """

    cdef public object tags
    cdef public object data
    cdef DataCollector parent

    cdef RunningState _state
    cdef timeval _tt_start
    cdef timeval _tt_end
    cdef long _tt_elapsed

    property started:
        """Tell if timer is started"""
        def __get__(self):
            return self._state == running

    property elapsed:
        """Returns the elapsed time in seconds"""
        def __get__(self):
            if self._state == running:
                gettimeofday(&self._tt_end, NULL)
                self._tt_elapsed = (self._tt_end.tv_sec-self._tt_start.tv_sec) * 1000000 + self._tt_end.tv_usec-self._tt_start.tv_usec
                return <float>self._tt_elapsed / 1000000
            elif self._state == finished:
                return <float>self._tt_elapsed / 1000000
            return None

    def __cinit__(self):
        self._state = initialized

    def __init__(self, object tags, DataCollector parent=None):
        """
        Tags values can be any scalar, mapping, sequence or callable.
        In case of a callable, redered value must be a sequence.

        :param tags: each values can be any scalar, mapping, sequence or
                     callable. In case of a callable, rendered value must
                     be a sequence.
        """
        self.tags = dict(tags)
        self.parent = parent
        self.data = None

    cpdef delete(self):
        """Discards timer from parent
        """
        if self.parent:
            self.parent.timers.discard(self)

    cpdef clone(self):
        """Clones timer
        """
        cdef Timer instance
        instance = Timer(self.tags, self.parent)
        if self.data:
            instance.data = self.data

        if self.parent:
            self.parent.timers.add(instance)
        return instance

    cpdef start(self):
        """Starts timer"""
        if self._state == running:
            raise RuntimeError('Already started')
        self._state = running
        gettimeofday(&self._tt_start, NULL)
        return self

    cpdef stop(self):
        """Stops timer"""
        if self._state != running:
            raise RuntimeError('Not started')
        gettimeofday(&self._tt_end, NULL)
        self._tt_elapsed = (self._tt_end.tv_sec-self._tt_start.tv_sec) * 1000000 + self._tt_end.tv_usec-self._tt_start.tv_usec
        self._state = finished
        return self

    cpdef __enter__(self):
        """Acts as a context manager.
        Automatically starts timer
        """
        if not self.started:
            self.start()
        return self

    def __exit__(self, object exc_type, object exc_value, object traceback):
        """Closes context manager.
        Automatically stops timer
        """
        if self.started:
            self.stop()

    def __call__(self, object func):
        """Acts as a decorator.
        Automatically starts and stops timer's clone.
        Example::

            @pynba.timer(foo=bar)
            def function_to_be_timed(self):
                pass
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self.clone():
                response = func(*args, **kwargs)
            return response
        return wrapper

    def __repr__(self):
        label, period = '', ''
        if self.elapsed:
            label = ' elapsed:'
            period = self.elapsed
        elif self._state == running:
            label = ' started:'
            period = '{tv_sec}.{tv_usec}'.format(self._tt_start)

        return '<{0}({1}){2}{3}>'.format(
            self.__class__.__name__,
            self.tags,
            label, period)


cdef class DataCollector(object):
    """
    This is the main data container.

    :param scriptname: the current scriptname
    :param hostname: the current hostname

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

    cdef public bint enabled
    cdef public set timers
    cdef public char*  scriptname
    cdef public char*  hostname
    cdef object _start
    cdef public object document_size
    cdef public object memory_peak

    cdef RunningState _state
    cdef timeval _tt_start
    cdef timeval _tt_end
    cdef long _tt_elapsed

    property started:
        """Tell if timer is started"""
        def __get__(self):
            return self._state == running

    property elapsed:
        """Returns the elapsed time in seconds"""
        def __get__(self):
            if self._state == running:
                gettimeofday(&self._tt_end, NULL)
                self._tt_elapsed = (self._tt_end.tv_sec-self._tt_start.tv_sec) * 1000000 + self._tt_end.tv_usec-self._tt_start.tv_usec
                return <float>self._tt_elapsed / 1000000
            elif self._state == finished:
                return <float>self._tt_elapsed / 1000000
            return None

    def __cinit__(self):
        self._state = initialized

    def __init__(self, object scriptname=None, object hostname=None):
        self.enabled = True
        self.timers = set()
        self.scriptname = scriptname
        self.hostname = hostname

        #: You can use this placeholder to store the real document size
        self.document_size = None
        #: You can use this placeholder to store the memory peak
        self.memory_peak = None

    cpdef start(self):
        """Starts"""
        if self._state == running:
            raise RuntimeError('Already started')
        self._state = running
        gettimeofday(&self._tt_start, NULL)

    cpdef stop(self):
        """Stops current elapsed time and every attached timers.
        """
        cdef Timer timer

        if self._state != running:
            raise RuntimeError('Not started')
        self._state = finished

        gettimeofday(&self._tt_end, NULL)
        self._tt_elapsed = (self._tt_end.tv_sec-self._tt_start.tv_sec) * 1000000 + self._tt_end.tv_usec-self._tt_start.tv_usec

        for timer in self.timers:
            if timer.started:
                timer.stop()

    def timer(self, **tags):
        """Factory new timer.
        """
        cdef Timer timer
        timer = Timer(tags, self)
        self.timers.add(timer)

        return timer

    cpdef flush(self):
        """Flushs.
        """
        logger.debug('flush', extra={
            'timers': self.timers,
            'elapsed': self.elapsed,
        })

        gettimeofday(&self._tt_start, NULL)
        self._state = running

        self.timers.clear()

