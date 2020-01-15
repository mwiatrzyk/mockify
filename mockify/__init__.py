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

version = (0, 6, 0)   # TODO: rename to __version__
