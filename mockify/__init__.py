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

from ._engine import Call, LocationInfo, Session, Expectation
from ._assert import assert_satisfied
from ._contextmanagers import ordered, satisfied, patched

try:
    from ._version import version as __version__
except ImportError:
    __version__ = (1, 0, 0)  # Fallback; should be kept up to date with most recent tag

__all__ = [
    'Call', 'LocationInfo', 'Session', 'Expectation', 'assert_satisfied',
    'ordered', 'satisfied', 'patched'
]
