# ---------------------------------------------------------------------------
# mockify/__init__.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

"""Library core module."""

from ._engine import assert_satisfied, Call, Expectation, Registry

__all__ = ['Call', 'Expectation', 'Registry', 'assert_satisfied']

version = (0, 6, 0)
