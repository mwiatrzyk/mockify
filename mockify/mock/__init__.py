# ---------------------------------------------------------------------------
# mockify/mock/__init__.py
#
# Copyright (C) 2019 - 2024 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
"""Classes and functions used to create mocks.

Each of these can be considered as a frontend on top of
:class:`mockify.core.Session` class, which is acting as a sort of backend for
mock classes.
"""

from ._abc_mock import ABCMock
from ._base import BaseMock
from ._factory import MockFactory
from ._function import BaseFunctionMock, FunctionMock
from ._mock import Mock

__all__ = ["BaseMock", "ABCMock", "MockFactory", "BaseFunctionMock", "FunctionMock", "Mock"]
