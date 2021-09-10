# ---------------------------------------------------------------------------
# mockify/core/__init__.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
"""Classes and functions providing Mockify's core functionality."""

from mockify import _utils
from mockify.mock import _base

from ._call import Call, LocationInfo
from ._expectation import Expectation
from ._functions import assert_satisfied, ordered, patched, satisfied
from ._inspect import MockInfo
from ._session import Session

BaseMock = _utils.mark_import_deprecated(
    _base.BaseMock, 'mockify.core.BaseMock', 'mockify.mock.BaseMock', '0.13'
)

__all__ = [
    'MockInfo', 'BaseMock', 'Call', 'LocationInfo', 'Expectation', 'Session',
    'assert_satisfied', 'satisfied', 'ordered', 'patched'
]
