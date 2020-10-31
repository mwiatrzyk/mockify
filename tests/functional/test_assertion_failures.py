# ---------------------------------------------------------------------------
# tests/functional/test_assertion_failures.py
#
# Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
"""These tests are used to check if valid errors are reported in various
situations."""

import pytest

from mockify import Call, exc, satisfied
from mockify.actions import Return
from mockify.cardinality import AtLeast, Exactly
from mockify.mock import Mock

_args_and_kwargs = [
    (tuple(), {}),
    ((1, 2), {}),
    ((1, 2), {
        'c': 3
    }),
    (('a', 'b'), {
        'spam': 'c',
        'more_spam': 123
    }),
]


def assert_attr_match(obj, **attrs):
    for name, expected_value in attrs.items():
        assert getattr(obj, name) == expected_value


@pytest.fixture
def mock():
    return Mock('mock')


@pytest.mark.parametrize('args, kwargs', _args_and_kwargs)
def test_when_mock_is_called_without_expectations_set__then_uninterested_call_is_raised(
    mock, args, kwargs
):
    with pytest.raises(exc.UninterestedCall) as excinfo:
        mock(*args, **kwargs)
    assert excinfo.value.actual_call == Call('mock', *args, **kwargs)


def test_when_mock_is_called_with_params_that_does_not_match_expectation__then_unexpected_call_is_raised(
    mock
):
    expectation = mock.expect_call(1, 2)
    with pytest.raises(exc.UnexpectedCall) as excinfo:
        mock(1, 2, 3)
    value = excinfo.value
    assert value.actual_call == Call('mock', 1, 2, 3)
    assert len(value.expected_calls) == 1
    assert value.expected_calls[0] == expectation.expected_call


def test_when_mock_is_called_less_times_than_expected__then_unsatisfied_is_raised(
    mock
):
    mock.expect_call()
    with pytest.raises(exc.Unsatisfied) as excinfo:
        with satisfied(mock):
            pass
    expectations = excinfo.value.unsatisfied_expectations
    assert len(expectations) == 1
    assert_attr_match(
        expectations[0],
        expected_call=Call('mock'),
        actual_call_count=0,
        expected_call_count=Exactly(1)
    )


def test_when_mock_is_called_more_times_than_expected__then_unsatisfied_is_raised(
    mock
):
    mock.expect_call()
    with pytest.raises(exc.Unsatisfied) as excinfo:
        with satisfied(mock):
            for _ in range(2):
                mock()
    expectations = excinfo.value.unsatisfied_expectations
    assert len(expectations) == 1
    assert_attr_match(
        expectations[0],
        expected_call=Call('mock'),
        actual_call_count=2,
        expected_call_count=Exactly(1)
    )


def test_when_mock_has_two_expectations_and_was_never_called__then_unsatisfied_is_raised(
    mock
):
    mock.expect_call(1)
    mock.expect_call(2)
    with pytest.raises(exc.Unsatisfied) as excinfo:
        with satisfied(mock):
            pass
    expectations = excinfo.value.unsatisfied_expectations
    assert len(expectations) == 2
    for i in range(2):
        assert_attr_match(
            expectations[i],
            expected_call=Call('mock', i + 1),
            actual_call_count=0,
            expected_call_count=Exactly(1)
        )


def test_when_mock_has_two_expectations_and_one_was_called__then_unsatisfied_is_raised(
    mock
):
    mock.expect_call(1)
    mock.expect_call(2)
    with pytest.raises(exc.Unsatisfied) as excinfo:
        with satisfied(mock):
            mock(1)
    expectations = excinfo.value.unsatisfied_expectations
    assert len(expectations) == 1
    assert_attr_match(
        expectations[0],
        expected_call=Call('mock', 2),
        actual_call_count=0,
        expected_call_count=Exactly(1)
    )


def test_when_mock_has_two_expectations_and_one_was_called_more_times_than_expected__then_unsatisfied_is_raised(
    mock
):
    mock.expect_call(1)
    mock.expect_call(2)
    with pytest.raises(exc.Unsatisfied) as excinfo:
        with satisfied(mock):
            mock(1)
            for _ in range(2):
                mock(2)
    expectations = excinfo.value.unsatisfied_expectations
    assert len(expectations) == 1
    assert_attr_match(
        expectations[0],
        expected_call=Call('mock', 2),
        actual_call_count=2,
        expected_call_count=Exactly(1)
    )


def test_when_mock_has_action_defined_to_be_called_once_and_is_never_called__then_unsatisfied_is_raised(
    mock
):
    mock.expect_call().will_once(Return(1))
    with pytest.raises(exc.Unsatisfied) as excinfo:
        with satisfied(mock):
            pass
    expectations = excinfo.value.unsatisfied_expectations
    assert len(expectations) == 1
    assert_attr_match(
        expectations[0],
        expected_call=Call('mock'),
        actual_call_count=0,
        expected_call_count=Exactly(1),
        action=Return(1)
    )


def test_when_mock_has_two_single_actions_defined_and_is_never_called__then_unsatisfied_is_raised(
    mock
):
    mock.expect_call().will_once(Return(1)).will_once(Return(2))
    with pytest.raises(exc.Unsatisfied) as excinfo:
        with satisfied(mock):
            pass
    expectations = excinfo.value.unsatisfied_expectations
    assert len(expectations) == 1
    assert_attr_match(
        expectations[0],
        expected_call=Call('mock'),
        actual_call_count=0,
        expected_call_count=Exactly(2),
        action=Return(1)
    )


def test_when_mock_has_two_single_actions_defined_and_is_called_once__then_first_action_is_consumed_and_unsatisfied_is_raised(
    mock
):
    mock.expect_call().will_once(Return(1)).will_once(Return(2))
    with pytest.raises(exc.Unsatisfied) as excinfo:
        with satisfied(mock):
            assert mock() == 1
    expectations = excinfo.value.unsatisfied_expectations
    assert len(expectations) == 1
    assert_attr_match(
        expectations[0],
        expected_call=Call('mock'),
        actual_call_count=1,
        expected_call_count=Exactly(2),
        action=Return(2)
    )


def test_when_mock_has_one_action_but_is_called_twice__then_oversaturated_call_is_raised(
    mock
):
    mock.expect_call().will_once(Return(1))
    with pytest.raises(exc.OversaturatedCall) as excinfo:
        assert mock() == 1
        mock()
    value = excinfo.value
    assert value.actual_call == Call('mock')
    assert_attr_match(
        value.oversaturated_expectation,
        expected_call=Call('mock'),
        actual_call_count=1,
        expected_call_count=Exactly(1)
    )


def test_if_mock_has_same_action_recorded_twice_using_will_once_and_is_not_called__then_expected_call_count_is_two(
    mock
):
    mock.expect_call().will_once(Return(1)).will_once(Return(1))
    with pytest.raises(exc.Unsatisfied) as excinfo:
        with satisfied(mock):
            pass
    expectations = excinfo.value.unsatisfied_expectations
    assert_attr_match(
        expectations[0],
        expected_call=Call('mock'),
        actual_call_count=0,
        expected_call_count=Exactly(2),
        action=Return(1)
    )


def test_if_mock_has_same_action_recorded_twice_using_will_once_and_is_called_once__then_expected_call_count_is_two(
    mock
):
    mock.expect_call().will_once(Return(1)).will_once(Return(1))
    with pytest.raises(exc.Unsatisfied) as excinfo:
        with satisfied(mock):
            assert mock() == 1
    expectations = excinfo.value.unsatisfied_expectations
    assert_attr_match(
        expectations[0],
        expected_call=Call('mock'),
        actual_call_count=1,
        expected_call_count=Exactly(2),
        action=Return(1)
    )


def test_if_mock_has_same_action_recorded_twice_using_will_once_and_again_using_will_repeatedly__then_expected_call_count_is_at_least_twice(
    mock
):
    mock.expect_call().will_once(Return(1)
                                 ).will_once(Return(1)
                                             ).will_repeatedly(Return(1))
    with pytest.raises(exc.Unsatisfied) as excinfo:
        with satisfied(mock):
            pass
    expectations = excinfo.value.unsatisfied_expectations
    assert_attr_match(
        expectations[0],
        expected_call=Call('mock'),
        actual_call_count=0,
        expected_call_count=AtLeast(2),
        action=Return(1)
    )
