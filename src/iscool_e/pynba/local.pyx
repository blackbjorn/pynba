# -*- coding: utf-8 -*-
"""
    IsCool-e Pynba
    ~~~~~~~~~~~~~~

    :copyright: (c) 2012 by IsCool Entertainment.
    :license: MIT, see LICENSE for more details.
"""

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        try:
            from dummy_thread import get_ident
        except ImportError:
            from _dummy_thread import get_ident


__all__ = ['LOCAL_STACK']

cdef class LocalStack(object):
    cdef dict stacked
    cdef object indent_func

    def __cinit__(self):
        self.stacked = {}
        self.indent_func = get_ident

    property indent:
        def __get__(self):
            return self.indent_func()

    property pynba:
        def __get__(self):
            return self.stacked.get(self.indent, None)

        def __set__(self, pynba):
            self.stacked[self.indent] = pynba

        def __del__(self):
            try:
                del self.stacked[self.indent]
            except KeyError:
                pass

LOCAL_STACK = LocalStack()
