# ---------------------------------------------------------------------------
# tests/unit/test_contextmanagers.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import pytest

from mockify.core import ordered, satisfied
from mockify.mock import Mock, MockFactory


class TestOrdered:

    def test_when_called_with_mocks_that_does_not_share_one_session__then_raise_type_error(self):
        first = Mock("first")
        second = Mock("second")
        with pytest.raises(TypeError) as excinfo:
            with ordered(first, second):
                first()
                second()
        assert str(excinfo.value) == "Mocks 'first' and 'second' have to use same session object"

    def test_run_ordered_expectations_for_two_distinct_mocks(self):
        factory = MockFactory()
        first, second = factory.mock("first"), factory.mock("second")
        first.expect_call(1, 2)
        second.expect_call()
        with satisfied(factory):
            with ordered(first, second):
                first(1, 2)
                second()
