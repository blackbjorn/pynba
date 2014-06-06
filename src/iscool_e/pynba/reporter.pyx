# -*- coding: utf-8 -*-
"""
    IsCool-e Pynba
    ~~~~~~~~~~~~~~

    :copyright: (c) 2012 by IsCool Entertainment.
    :license: MIT, see LICENSE for more details.
"""

from socket import socket, AF_INET, SOCK_DGRAM, gaierror
import collections
from .log import logger
from .message import dumps


cpdef Reporter_prepare(servername, hostname, scriptname, elapsed, list timers,
            ru_utime=None, ru_stime=None, document_size=None,
            memory_peak=None, status=None, memory_footprint=None, schema=None):
    """Prepares the message
    """

    cdef object msg
    cdef list dictionary
    cdef object timer
    cdef int tag_count
    cdef object name
    cdef object value

    logger.debug("prepare protobuff", extra={
        'servername': servername,
        'hostname': hostname,
        'scriptname': scriptname,
        'elapsed': elapsed,
        'timers': timers
    })

    msg = {
        'hostname': hostname if hostname else '',
        'server_name': servername if servername else '',
        'script_name': scriptname if scriptname else '',
        'request_count': 1,
        'document_size': document_size if document_size else 0,
        'memory_peak': memory_peak if memory_peak else 0,
        'request_time': elapsed,
        'ru_utime': ru_utime if ru_utime else 0.0,
        'ru_stime': ru_stime if ru_stime else 0.0,
        'status': status if status else 200,
        'memory_footprint': memory_footprint if memory_footprint else 0,
        'schema': schema if schema else '',
    }

    if timers:
        dictionary = [] # contains mapping of tags name or value => uniq id
        timer_hit_count = []
        timer_value = []
        timer_tag_name = []
        timer_tag_value = []
        timer_tag_count = []

        for timer in timers:
            # Add a single timer
            timer_hit_count.append(1)
            timer_value.append(timer.elapsed)

            # Encode associated tags
            tag_count = 0
            for name, value in flattener(timer.tags):
                if name not in dictionary:
                    dictionary.append(name)
                if value not in dictionary:
                    dictionary.append(value)
                timer_tag_name.append(dictionary.index(name))
                timer_tag_value.append(dictionary.index(value))
                tag_count += 1

            # Number of tags
            timer_tag_count.append(tag_count)

        msg.update({
            'dictionary': dictionary,
            'timer_hit_count': timer_hit_count,
            'timer_value': timer_value,
            'timer_tag_name': timer_tag_name,
            'timer_tag_value': timer_tag_value,
            'timer_tag_count': timer_tag_count,
        })

    # Send message to Pinba server
    return dumps(**msg)


cdef class Reporter(object):
    """Formats and send report to pinba server.

    :param address: the address to the udp server.
    :param raise_on_fail: raise exception on fail.
    """

    cdef public object address
    cdef public object sock
    cdef public object raise_on_fail

    def __init__(self, address, raise_on_fail=False):
        self.address = address
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.raise_on_fail = raise_on_fail

    def __call__(self, server_name, hostname, script_name,
            elapsed, list timers, ru_utime=None, ru_stime=None,
            document_size=None, memory_peak=None, status=None,
            memory_footprint=None, schema=None):
        """
        Same as PHP pinba_flush()
        """

        msg = Reporter.prepare(server_name, hostname, script_name, elapsed,
                               timers, ru_utime, ru_stime, document_size,
                               memory_peak, status, memory_footprint, schema)
        self.send(msg)

    prepare = staticmethod(Reporter_prepare)

    def send(self, msg):
        """Sends message to pinba server"""
        try:
            return self.sock.sendto(msg, self.address)
        except Exception as error:
            if self.raise_on_fail:
                raise
            logger.exception(error)
        return None


cpdef flattener(dict tags):
    """
    Flatten tags Mapping into a list of tuple.
    :tags: must be a Mapping that implements iteritems()

    >>> flattener({'foo': 'bar'})
    [('foo', 'bar')]
    >>> flattener({'foo': 12})
    [('foo', '12')]
    >>> flattener({'foo': [12, 13]})
    [('foo', '12'), ('foo', '13')]
    >>> flattener({'foo': [12]})
    [('foo', '12')]
    >>> flattener({'foo': [12]})
    [('foo', '12')]
    >>> flattener({'foo': {'foo': [12]}})
    [('foo.foo', '12')]
    >>> flattener({'foo': lambda : ['bar', 'baz']})
    [('foo', 'bar'), ('foo', 'baz')]
    >>> flattener({'foo': {42: [12]}})
    [('foo.42', '12')]

    """
    cdef set data

    data = set(flatten(tags, ''))
    return sorted([(key, str(value)) for key, value in data])

cdef inline list flatten(dict tags, str namespace):
    """Flatten recursively"""
    cdef object pref
    cdef object key
    cdef object value
    cdef list values
    cdef list output

    if len(namespace):
        pref = str(namespace + ".")
    else:
        pref = str('')

    output = []
    for key, value in tags.items():
        if isinstance(value, collections.Callable):
            value = value()
        try:
            if isinstance(value, (list, tuple, set)):
                values = [(pref + str(key), v) for v in set(value)]
                output.extend(values)
            elif isinstance(value, dict):
                output.extend(flatten(value, key))
            else:
                output.append((pref + str(key), value))
        except TypeError as error:
            logger.exception(error)

    return output
