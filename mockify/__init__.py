# ---------------------------------------------------------------------------
# mockify/__init__.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
"""Library core module."""

from pkg_resources import DistributionNotFound, get_distribution

from .core import (
    Call, Expectation, LocationInfo, Session, assert_satisfied, ordered,
    patched, satisfied
)

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = '0.8.0'  # Fallback; keep this up to date with most recent tag

__all__ = [
    'Call', 'LocationInfo', 'Session', 'Expectation', 'assert_satisfied',
    'ordered', 'satisfied', 'patched'
]
