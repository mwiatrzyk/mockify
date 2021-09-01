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

from ._abc_mock import ABCMock
from ._factory import MockFactory
from ._function import FunctionMock, BaseFunctionMock
from ._mock import Mock
from ._object import ObjectMock

__all__ = ['Mock', 'ObjectMock', 'FunctionMock', 'BaseFunctionMock', 'MockFactory', 'ABCMock']
