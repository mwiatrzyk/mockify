# ---------------------------------------------------------------------------
# mockify/mock.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
from ._base import MockInfo, BaseMock
from ._mock import Mock
from ._function import FunctionMock
from ._factory import MockFactory
from ._abc_mock import ABCMock

__all__ = ['MockInfo', 'BaseMock', 'Mock', 'FunctionMock', 'MockFactory', 'ABCMock']
