# ---------------------------------------------------------------------------
# tests/conftest.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import os
import sys
import functools
import collections

import pytest

this_dir = os.path.abspath(os.path.dirname(__file__))
src_dir = os.path.join(this_dir, '..', 'src')
sys.path.append(src_dir)

from mockify import Registry
from mockify.mock import Namespace, Function


@pytest.fixture
def mock_registry():
    registry = Registry()
    yield registry
    registry.assert_satisfied()


@pytest.fixture
def mock_factory(mock_registry):

    class Factory:

        def namespace(self, name):
            return Namespace(name, registry=mock_registry)

        def function(self, name):
            return Function(name, registry=mock_registry)

    return Factory()
