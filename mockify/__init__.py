# ---------------------------------------------------------------------------
# mockify/__init__.py
#
# Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
"""Library core module.

.. deprecated:: 0.9.0
    To import Mockify's core functionality, import from :mod:`mockify.core`
    module instead.
"""

from pkg_resources import DistributionNotFound, get_distribution

from .core import (  # TODO: remove from here; import from mockify.core explicitly instead
    Call, Expectation, LocationInfo, Session, assert_satisfied, ordered,
    patched, satisfied)

__author__ = 'Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>'
__released__ = 2019
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = '0.11.0'  # Use 'inv tag' to update this

__all__ = [
    'Call', 'LocationInfo', 'Session', 'Expectation', 'assert_satisfied',
    'ordered', 'satisfied', 'patched'
]
