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
"""Library core module."""

from ._call import Call, LocationInfo
from ._expectation import Expectation
from ._session import Session

from ._functions import *

from mockify import _utils
from mockify.mock import _base

MockInfo = _utils.mark_import_deprecated(_base.MockInfo, 'mockify.core.MockInfo', 'mockify.mock.MockInfo', '(unreleased)')
BaseMock = _utils.mark_import_deprecated(_base.BaseMock, 'mockify.core.BaseMock', 'mockify.mock.BaseMock', '(unreleased)')

__all__ = [
    'assert_satisfied', 'Call', 'LocationInfo', 'satisfied', 'ordered',
    'patched', 'Expectation', 'Session'
]
