# ---------------------------------------------------------------------------
# tests/functional/test_basic_functionality.py
#
# Copyright (C) 2019 - 2024 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import pytest

from mockify import exc
from mockify.api import FunctionMock, Mock


@pytest.fixture(
    params=[
        lambda: FunctionMock("mock"),
        lambda: Mock("mock"),
    ]
)
def mock(request):
    return request.param()


def test_when_mock_called_without_expectation_set_then_raise_uninterested_call_exception(mock, assert_that):
    with pytest.raises(exc.UninterestedCall) as excinfo:
        mock(1, 2, c=3)
    assert_that.call_params_match(excinfo.value.actual_call, 1, 2, c=3)


def test_when_mock_called_with_parameters_that_does_not_match_any_expectation_then_raise_unexpected_call_exception(
    mock, assert_that
):
    mock.expect_call(1, 2)
    mock.expect_call(1, 2, c=3)
    with pytest.raises(exc.UnexpectedCall) as excinfo:
        mock(1, 2, 3)
    assert_that.call_params_match(excinfo.value.actual_call, 1, 2, 3)
    assert len(excinfo.value.expected_calls) == 2
    first_expected, second_expected = excinfo.value.expected_calls
    assert_that.call_params_match(first_expected, 1, 2)
    assert_that.call_params_match(second_expected, 1, 2, c=3)
