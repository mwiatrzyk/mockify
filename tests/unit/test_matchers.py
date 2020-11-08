# ---------------------------------------------------------------------------
# tests/unit/test_matchers.py
#
# Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import collections

import pytest

from mockify import exc
from mockify.core import Call, satisfied
from mockify.matchers import AnyOf, Func, List, Object, Regex, Type, _
from mockify.mock import Mock


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

    @pytest.mark.parametrize(
        'types, expected_repr', [
            ((int, ), "mock(Type(int))"),
            ((int, float), "mock(Type(int, float))"),
        ]
    )
    def test_expected_call_formatting(self, types, expected_repr):
        mock = Mock('mock')
        expectation = mock.expect_call(Type(*types))
        assert str(expectation.expected_call) == expected_repr

    def test_successful_match(self):
        mock = Mock('mock')
        mock.expect_call(Type(int))
        with satisfied(mock):
            mock(123)

    def test_when_mock_call_does_not_match_expectation__then_fail_with_unexpected_call_error(
        self
    ):
        mock = Mock('mock')
        mock.expect_call(Type(int))
        with pytest.raises(exc.UnexpectedCall) as excinfo:
            with satisfied(mock):
                mock('spam')
        value = excinfo.value
        assert value.actual_call == Call('mock', 'spam')
        assert len(value.expected_calls) == 1
        assert str(value.expected_calls[0]) == "mock(Type(int))"

    def test_when_matcher_is_created_without_args__then_fail_with_type_error(
        self
    ):
        with pytest.raises(TypeError) as excinfo:
            Type()
        assert str(
            excinfo.value
        ) == "__init__() requires at least 1 positional argument, got 0"

    def test_when_matcher_is_created_with_something_that_is_not_a_type__then_fail_with_type_error(
        self
    ):
        with pytest.raises(TypeError) as excinfo:
            Type('spam')
        assert str(
            excinfo.value
        ) == "__init__() requires type instances, got 'spam'"


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
        assert str(
            expectation.expected_call
        ) == "mock(Type(int, float) | 'spam')"

    def test_successful_match(self):
        mock = Mock('mock')
        mock.expect_call(Type(int) | 'spam').times(2)
        with satisfied(mock):
            mock(123)
            mock('spam')

    def test_successful_match_against_triple_alternative(self):
        mock = Mock('mock')
        mock.expect_call(Type(int) | Type(float) | 'spam').times(3)
        with satisfied(mock):
            mock(123)
            mock(3.14)
            mock('spam')

    def test_when_match_is_not_found__then_raise_unexpected_call_error(self):
        mock = Mock('mock')
        mock.expect_call(Type(int) | 'spam')
        with pytest.raises(exc.UnexpectedCall) as excinfo:
            with satisfied(mock):
                mock(3.14)
        value = excinfo.value
        assert value.actual_call == Call('mock', 3.14)
        assert len(value.expected_calls) == 1
        assert str(value.expected_calls[0]) == "mock(Type(int) | 'spam')"


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


class TestList:

    @pytest.mark.parametrize(
        'args, kwargs, expected_repr', [
            ((Type(str), ), {}, "List(Type(str))"),
            ((Type(str), ), {
                'min_length': 2
            }, "List(Type(str), min_length=2)"),
            ((Type(str), ), {
                'max_length': 4
            }, "List(Type(str), max_length=4)"),
            (
                (Type(str), ), {
                    'min_length': 2,
                    'max_length': 4
                }, "List(Type(str), min_length=2, max_length=4)"
            ),
        ]
    )
    def test_repr(self, args, kwargs, expected_repr):
        assert repr(List(*args, **kwargs)) == expected_repr

    @pytest.mark.parametrize('non_matching', [123, 'abc'])
    def test_there_is_no_match_if_value_is_not_a_list(self, non_matching):
        assert List(_) != non_matching

    @pytest.mark.parametrize('non_matching', [
        [1, 2, 3],
        [1, 2, '3'],
    ])
    def test_there_is_no_match_if_list_containing_one_or_more_values_that_does_not_match_given_matcher(
        self, non_matching
    ):
        assert List(Type(str)) != non_matching

    def test_there_is_no_match_if_number_of_items_is_greater_than_expected_maximum(
        self
    ):
        assert List(Type(str), max_length=1) != ['1', '2']

    def test_there_is_no_match_if_number_of_items_is_less_than_expected_minimum(
        self
    ):
        assert List(Type(str), min_length=3) != ['1', '2']

    def test_there_is_no_match_if_number_of_items_is_less_than_expected_minimum_or_greater_than_expected_maximum(
        self
    ):
        uut = List(Type(str), min_length=1, max_length=2)
        assert uut != []
        assert uut == ['1']
        assert uut == ['1', '2']
        assert uut != ['1', '2', '3']

    def test_there_is_a_match_if_value_is_a_list_containing_all_elements_matching_given_matcher(
        self
    ):
        assert List(Type(str)) == ['1', '2', '3']


class TestObject:
    Reference = collections.namedtuple('Reference', 'x,y,z')

    @pytest.mark.parametrize(
        'kwargs, expected_repr', [
            ({
                'a': 1
            }, "Object(a=1)"),
            ({
                'a': 1,
                'b': 'spam'
            }, "Object(a=1, b='spam')"),
        ]
    )
    def test_repr(self, kwargs, expected_repr):
        assert repr(Object(**kwargs)) == expected_repr

    def test_matcher_must_have_at_least_one_keyword_arg_given(self):
        with pytest.raises(TypeError) as excinfo:
            Object()
        assert str(
            excinfo.value
        ) == '__init__ must be called with at least 1 named argument'

    def test_matcher_is_equal__if_all_given_attrs_are_the_same(self):
        assert self.Reference(1, 2, 3) == Object(x=1, y=2, z=3)

    def test_matcher_is_equal__if_subset_of_given_attrs_is_the_same(self):
        assert self.Reference(1, 2, 3) == Object(x=1, y=2)

    def test_matcher_is_not_equal__if_not_all_given_attrs_are_the_same(self):
        assert self.Reference(1, 2, 3) != Object(x=1, y=2, z=4)

    def test_matcher_is_not_equal__if_contains_more_attrs_than_reference_object(
        self
    ):
        assert self.Reference(1, 2, 3) != Object(x=1, y=2, z=3, w=4)

    def test_matcher_is_not_equal__if_reference_does_not_have_given_property(
        self
    ):
        assert self.Reference(1, 2, 3) != Object(foo=_)

    def test_matcher_is_equal__when_any_matcher_is_used_as_an_argument_and_comparison_with_always_inequal_object_is_made(
        self
    ):

        class AlwaysInequalObject:

            def __eq__(self, other):
                return False

        class Foo:

            def __init__(self):
                self.val = AlwaysInequalObject()

        foo = Foo()

        assert Object(val=_) == foo
