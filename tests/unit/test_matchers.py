# ---------------------------------------------------------------------------
# tests/unit/test_matchers.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import pytest

from mockify import exc, satisfied, Call
from mockify.mock import Mock
from mockify.matchers import _, Type, Regex, AnyOf, Func


class TestAny:
    _matching_values = [1, 3.14, 'spam']

    def test_expected_call_formatting(self):
        mock = Mock('mock')
        expectation = mock.expect_call(_)
        assert str(expectation.expected_call) == 'mock(_)'

    @pytest.mark.parametrize('value', _matching_values)
    def test_any_matcher_with_positional_argument(self, value):
        mock = Mock('mock')
        mock.expect_call(_)
        with satisfied(mock):
            mock(value)

    @pytest.mark.parametrize('value', _matching_values)
    def test_any_matcher_with_keyword_argument(self, value):
        mock = Mock('mock')
        mock.expect_call(foo=_)
        with satisfied(mock):
            mock(foo=value)

    @pytest.mark.parametrize('value', _matching_values)
    def test_any_matcher_with_structured_value(self, value):
        mock = Mock('mock')
        mock.expect_call({'spam': _})
        with satisfied(mock):
            mock({'spam': value})


class TestType:

    @pytest.mark.parametrize('types, expected_repr', [
        ((int,), "mock(Type(int))"),
        ((int, float), "mock(Type(int, float))"),
    ])
    def test_expected_call_formatting(self, types, expected_repr):
        mock = Mock('mock')
        expectation = mock.expect_call(Type(*types))
        assert str(expectation.expected_call) == expected_repr

    def test_successful_match(self):
        mock = Mock('mock')
        mock.expect_call(Type(int))
        with satisfied(mock):
            mock(123)

    def test_when_mock_call_does_not_match_expectation__then_fail_with_unexpected_call_error(self):
        mock = Mock('mock')
        mock.expect_call(Type(int))
        with pytest.raises(exc.UnexpectedCall) as excinfo:
            with satisfied(mock):
                mock('spam')
        value = excinfo.value
        assert value.actual_call == Call('mock', 'spam')
        assert len(value.expected_calls) == 1
        assert str(value.expected_calls[0]) == "mock(Type(int))"

    def test_when_matcher_is_created_without_args__then_fail_with_type_error(self):
        with pytest.raises(TypeError) as excinfo:
            Type()
        assert str(excinfo.value) == "__init__() requires at least 1 positional argument, got 0"

    def test_when_matcher_is_created_with_something_that_is_not_a_type__then_fail_with_type_error(self):
        with pytest.raises(TypeError) as excinfo:
            Type('spam')
        assert str(excinfo.value) == "__init__() requires type instances, got 'spam'"


class TestRegex:

    def test_expected_call_formatting(self):
        mock = Mock('mock')
        expectation = mock.expect_call(Regex(r'[0-9]+'))
        assert str(expectation.expected_call) == "mock(Regex('[0-9]+'))"

    def test_successful_match(self):
        mock = Mock('mock')
        mock.expect_call(Regex('[0-9]+'))
        with satisfied(mock):
            mock('0123456789')

    def test_when_match_is_not_found__then_raise_unexpected_call_error(self):
        mock = Mock('mock')
        mock.expect_call(Regex('[0-9]+'))
        with pytest.raises(exc.UnexpectedCall) as excinfo:
            with satisfied(mock):
                mock('spam')
        value = excinfo.value
        assert value.actual_call == Call('mock', 'spam')
        assert len(value.expected_calls) == 1
        assert str(value.expected_calls[0]) == "mock(Regex('[0-9]+'))"


class TestAnyOf:

    def test_expected_call_formatting(self):
        mock = Mock('mock')
        expectation = mock.expect_call(Type(int, float) | 'spam')
        assert str(expectation.expected_call) == "mock(Type(int, float)|'spam')"

    def test_successful_match(self):
        mock = Mock('mock')
        mock.expect_call(Type(int) | 'spam').times(2)
        with satisfied(mock):
            mock(123)
            mock('spam')

    def test_successful_match_against_triple_alternative(self):
        mock = Mock('mock')
        mock.expect_call(Type(int)|Type(float)|'spam').times(3)
        with satisfied(mock):
            mock(123)
            mock(3.14)
            mock('spam')

    def test_when_match_is_not_found__then_raise_unexpected_call_error(self):
        mock = Mock('mock')
        mock.expect_call(Type(int)|'spam')
        with pytest.raises(exc.UnexpectedCall) as excinfo:
            with satisfied(mock):
                mock(3.14)
        value = excinfo.value
        assert value.actual_call == Call('mock', 3.14)
        assert len(value.expected_calls) == 1
        assert str(value.expected_calls[0]) == "mock(Type(int)|'spam')"


class TestAllOf:

    def test_expected_call_formatting(self):
        mock = Mock('mock')
        expectation = mock.expect_call(Type(int) & 123)
        assert str(expectation.expected_call) == "mock(Type(int) & 123)"

    def test_successful_match(self):
        mock = Mock('mock')
        mock.expect_call(Type(int) & AnyOf(123, 456)).times(2)
        with satisfied(mock):
            mock(123)
            mock(456)

    def test_successful_match_against_triple_conjunction(self):
        mock = Mock('mock')
        mock.expect_call(
            Type(int) & Func(lambda x: x > 0) & Func(lambda x: x < 10)
        ).times(2)
        with satisfied(mock):
            mock(1)
            mock(9)
