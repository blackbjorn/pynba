# -*- coding: utf-8 -*-
"""
    IsCool-e Pynba
    ~~~~~~~~~~~~~~

    :copyright: (c) 2012 by IsCool Entertainment.
    :license: MIT, see LICENSE for more details.
"""

import resource
from .local import LOCAL_STACK
from .collector import DataCollector

cdef class RequestContext(object):
    """
    A new instance will be created every new request.

    :param reporter: a :class:`Reporter` instance
    :param environ: the current WSGI environ mapping
    :param config: may have these keys:
                   ``prefix`` will prepend scriptname
    """

    cdef public object reporter
    cdef public dict config
    cdef public object pynba
    cdef public object resources
    cdef str _scriptname
    cdef str _hostname
    cdef str _servername

    property scriptname:
        def __get__(self):
            cdef str out
            cdef object pynba
            out = self.config.get('prefix', '')

            if self.pynba:
                pynba = self.pynba
                if pynba.scriptname:
                    return out + self.pynba.scriptname
            return out + self._scriptname

    property hostname:
        def __get__(self):
            cdef object pynba
            if self.pynba:
                pynba = self.pynba
                if pynba.hostname:
                    return pynba.hostname
            if self._hostname:
                return self._hostname

            return None

    property servername:
        def __get__(self):
            return self._servername

    def __init__(self, object reporter, dict environ, **config):
        self.reporter = reporter

        #: config['prefix'] prepends the sent scriptname to pinba.
        self.config = config

        #: futur :class:`DataCollector`
        self.pynba = None
        #: will keep a snap of :func:`resource.getrusage`
        self.resources = None

        self._scriptname = environ.get('PATH_INFO', '')
        self._hostname = environ.get('SERVER_NAME', None)
        self._servername = environ.get('HTTP_HOST', None)

    cpdef push(self):
        """Pushes current context into local stack.
        """

        self.pynba = DataCollector(self._scriptname, self._hostname)
        self.pynba.start()
        LOCAL_STACK.pynba = self.pynba
        self.resources = resource.getrusage(resource.RUSAGE_SELF)

    cpdef pop(self):
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

    cpdef flush(self):
        """Flushes timers.

        Similar to the PHP ``pinba_flush()`` function.
        scriptname sent to pinba will be prepend by config['prefix']
        """

        cdef list timers
        cdef object timer
        cdef object document_size
        cdef object memory_peak
        cdef object usage
        cdef object ru_utime
        cdef object ru_stime

        if not self.pynba or not self.pynba.enabled:
            return

        self.pynba.stop()
        timers = [timer for timer in self.pynba.timers if timer.elapsed]
        document_size = self.pynba.document_size
        memory_peak = self.pynba.memory_peak
        usage = resource.getrusage(resource.RUSAGE_SELF)
        ru_utime = usage.ru_utime - self.resources.ru_utime
        ru_stime = usage.ru_stime - self.resources.ru_stime

        self.reporter(
            servername= self.servername,
            hostname= self.hostname,
            scriptname= self.scriptname,
            elapsed= self.pynba.elapsed,
            timers= timers,
            ru_utime= ru_utime,
            ru_stime= ru_stime,
            document_size= document_size,
            memory_peak= memory_peak
        )

        self.pynba.flush()
