# ---------------------------------------------------------------------------
# mockify/mock/__init__.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
"""Module containing types used to mock things.

These can be considered as frontends on top of Mockify's core
functionality.
"""

from mockify import _utils

from ._base import *
from ._abc_mock import *
from ._factory import *
from ._function import *
from ._mock import *

from . import _base, _abc_mock, _factory, _function, _mock

__all__ = _utils.merge_export_lists(_base, _abc_mock, _factory, _function, _mock)
