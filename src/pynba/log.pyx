# -*- coding: utf-8 -*-
"""
    Pynba
    ~~~~~

    :copyright: (c) 2015 by Xavier Barbosa.
    :license: MIT, see LICENSE for more details.
"""

import logging

# This was added in Python 2.7/3.2
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logger = logging.getLogger('pynba')
if not logger.handlers:
    logger.addHandler(NullHandler())

__all__ = ['logger']
