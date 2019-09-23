# ---------------------------------------------------------------------------
# mockify/mock/__init__.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

"""Classes for mocking things."""

from ._mock import Mock
from ._object import Object
from ._function import Function
from ._namespace import Namespace
from ._factory import *
from ._factory import __all__ as _factory_all

__all__ = ['Mock', 'Object', 'Function', 'Namespace'] + _factory_all
