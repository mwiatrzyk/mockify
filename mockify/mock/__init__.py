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

from ._object import Object
from ._function import Function, FunctionFactory

__all__ = ['Object', 'Function', 'FunctionFactory']
