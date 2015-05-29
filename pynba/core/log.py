"""
    Pynba
    ~~~~~

    :copyright: (c) 2015 by Xavier Barbosa.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import, unicode_literals

import logging

__all__ = ['logger']

logger = logging.getLogger('pynba')
if not logger.handlers:
    logger.addHandler(logging.NullHandler())
