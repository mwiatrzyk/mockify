# ---------------------------------------------------------------------------
# tests/engine/test_expectation.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import pytest

from _mockify import exc, Call, Expectation
from _mockify.cardinality import AtLeast, AtMost, Between


class ActionStub:

    def __init__(self, return_value):
        self._return_value = return_value

    def __str__(self):
        return "ActionStub({})".format(self._return_value)

    def __call__(self, call):
        return self._return_value


class TimesStub:

    def __init__(self, func, expected=None):
        self._expected = expected
        self._func = func

    def is_satisfied(self, actual):
        return self._func(actual)

    def format_expected(self):
        return self._expected


class TestBase:

    def setup_method(self):
        self.foo_call = Call('foo')
        self.bar_call = Call('bar')

    def expect_foo(self):
        self.uut = Expectation(self.foo_call, 'foo.py', 123)
        return self.uut

    def expect_bar(self):
        self.uut = Expectation(self.bar_call, 'bar.py', 456)
        return self.uut

    def call_foo(self):
        return self.uut(self.foo_call)


class TestBasicFunctionality(TestBase):

    def test_expected_call_property_contains_expected_call_constructor_argument(self):
        self.expect_foo()
        assert self.uut.expected_call is self.foo_call

    def test_format_location_returns_formatted_filename_and_lineno(self):
        self.expect_foo()
        filename, lineno = self.foo_call.location
        assert self.uut.format_location() == f"{filename}:{lineno}"

    def test_when_called_with_non_matching_call_object__then_raise_exception(self):
        self.expect_bar()
        with pytest.raises(TypeError):
            self.call_foo()


class TestIsSatisfied(TestBase):

    def test_newly_created_is_expected_to_be_called_once(self):
        self.expect_foo()
        assert not self.uut.is_satisfied()
        self.call_foo()
        assert self.uut.is_satisfied()
        self.call_foo()
        assert not self.uut.is_satisfied()

    def test_if_times_with_positive_int_value_called__it_is_expected_to_be_called_that_many_times(self):
        self.expect_foo().times(2)
        assert not self.uut.is_satisfied()
        for _ in range(2):
            self.call_foo()
        assert self.uut.is_satisfied()
        self.call_foo()
        assert not self.uut.is_satisfied()

    def test_if_times_with_zero_value_called__it_is_expected_to_be_never_called(self):
        self.expect_foo().times(0)
        assert self.uut.is_satisfied()
        self.call_foo()
        assert not self.uut.is_satisfied()

    def test_if_times_with_times_object_called__it_is_expected_to_be_called_according_to_times_object_used(self):
        self.expect_foo().times(TimesStub(lambda x: x >= 1))
        assert not self.uut.is_satisfied()
        self.call_foo()
        assert self.uut.is_satisfied()
        self.call_foo()
        assert self.uut.is_satisfied()

    def test_if_will_once_used_once__it_is_expected_to_invoke_given_action_once(self):
        self.expect_foo().will_once(ActionStub(1))
        assert not self.uut.is_satisfied()
        assert self.call_foo() == 1
        assert self.uut.is_satisfied()

    def test_if_will_once_used_twice__it_is_expected_to_invoke_actions_in_specified_order_twice(self):
        self.expect_foo().\
            will_once(ActionStub(1)).\
            will_once(ActionStub(2))
        assert not self.uut.is_satisfied()
        assert self.call_foo() == 1
        assert self.call_foo() == 2
        assert self.uut.is_satisfied()

    def test_if_will_once_used_twice_and_called_four_times__then_invoke_last_action_each_extra_time_and_make_it_not_satisfied(self):
        self.expect_foo().\
            will_once(ActionStub(1)).\
            will_once(ActionStub(2))
        assert not self.uut.is_satisfied()
        assert self.call_foo() == 1
        assert self.call_foo() == 2
        assert self.uut.is_satisfied()
        with pytest.raises(exc.OversaturatedCall):
            self.call_foo()
        assert not self.uut.is_satisfied()

    def test_if_will_repeatedly_used__then_expect_it_to_be_called_optionally_and_invoke_given_action_on_each_call(self):
        self.expect_foo().will_repeatedly(ActionStub(1))
        assert self.uut.is_satisfied()
        for _ in range(5):
            assert self.call_foo() == 1
        assert self.uut.is_satisfied()

    def test_if_will_repeatedly_used_with_times__then_expect_it_to_be_called_according_to_times(self):
        self.expect_foo().will_repeatedly(ActionStub(1)).times(2)
        assert not self.uut.is_satisfied()
        for _ in range(2):
            assert self.call_foo() == 1
        assert self.uut.is_satisfied()
        assert self.call_foo() == 1
        assert not self.uut.is_satisfied()

    def test_expect_it_to_repeatedly_invoke_action_twice_and_then_to_repeatedly_invoke_other_action(self):
        self.expect_foo().\
            will_repeatedly(ActionStub(1)).times(2).\
            will_repeatedly(ActionStub(2))
        assert not self.uut.is_satisfied()
        for _ in range(2):
            assert self.call_foo() == 1
        assert self.uut.is_satisfied()
        for _ in range(3):
            assert self.call_foo() == 2
        assert self.uut.is_satisfied()

    def test_expect_it_to_repeatedly_invoke_action_twice_and_then_to_once_execute_two_other_actions(self):
        self.expect_foo().\
            will_repeatedly(ActionStub(1)).times(2).\
            will_once(ActionStub(2)).\
            will_once(ActionStub(3))
        assert not self.uut.is_satisfied()
        for _ in range(2):
            assert self.call_foo() == 1
        assert not self.uut.is_satisfied()
        assert self.call_foo() == 2
        assert self.call_foo() == 3
        assert self.uut.is_satisfied()
        with pytest.raises(exc.OversaturatedCall):
            self.call_foo()
        assert not self.uut.is_satisfied()

    def test_expect_it_to_once_execute_given_action_and_then_execute_repeated_action_twice(self):
        self.expect_foo().\
            will_once(ActionStub(1)).\
            will_repeatedly(ActionStub(2)).times(2)
        assert not self.uut.is_satisfied()
        assert self.call_foo() == 1
        assert not self.uut.is_satisfied()
        for _ in range(2):
            assert self.call_foo() == 2
        assert self.uut.is_satisfied()
        assert self.call_foo() == 2
        assert not self.uut.is_satisfied()

    def test_expect_it_to_once_execute_given_action_and_then_execute_repeated_action_twice_and_then_execute_three_single_actions(self):
        self.expect_foo().\
            will_once(ActionStub(1)).\
            will_repeatedly(ActionStub(2)).times(2).\
            will_once(ActionStub(3)).\
            will_once(ActionStub(4)).\
            will_once(ActionStub(5))
        assert not self.uut.is_satisfied()
        assert self.call_foo() == 1
        assert not self.uut.is_satisfied()
        for _ in range(2):
            assert self.call_foo() == 2
        assert not self.uut.is_satisfied()
        assert self.call_foo() == 3
        assert self.call_foo() == 4
        assert self.call_foo() == 5
        assert self.uut.is_satisfied()
        with pytest.raises(exc.OversaturatedCall):
            self.call_foo()
        assert not self.uut.is_satisfied()


class TestFormatActual(TestBase):

    def test_each_time_expectation_is_called__actual_call_count_is_increased_by_one(self):
        self.expect_foo()
        assert self.uut.format_actual() == 'never called'
        self.call_foo()
        assert self.uut.format_actual() == 'called once'
        self.call_foo()
        assert self.uut.format_actual() == 'called twice'
        self.call_foo()
        assert self.uut.format_actual() == 'called 3 times'


class TestFormatExpected(TestBase):

    def test_newly_created_expectation_is_expected_to_be_called_once(self):
        self.expect_foo()
        assert self.uut.format_expected() == 'to be called once'

    def test_if_expectation_has_times_set__then_expected_call_count_is_the_one_taken_from_times_object(self):
        self.expect_foo().times(TimesStub(lambda x: x == 2, 'to be called twice'))
        assert self.uut.format_expected() == 'to be called twice'
        self.expect_foo().times(3)
        assert self.uut.format_expected() == 'to be called 3 times'

    def test_if_expectation_has_actions_recorded__then_expected_call_count_matches_number_of_actions_recorded(self):
        self.expect_foo().\
            will_once(ActionStub(1))
        assert self.uut.format_expected() == 'to be called once'
        self.expect_foo().\
            will_once(ActionStub(1)).\
            will_once(ActionStub(2))
        assert self.uut.format_expected() == 'to be called twice'
        self.expect_foo().\
            will_once(ActionStub(1)).\
            will_once(ActionStub(2)).\
            will_once(ActionStub(3))
        assert self.uut.format_expected() == 'to be called 3 times'

    def test_if_expectation_has_repeated_action_recorded__then_formatted_expected_is_none_as_it_can_be_called_optionally(self):
        self.expect_foo().will_repeatedly(ActionStub(1))
        assert self.uut.format_expected() is None

    def test_if_expectation_has_repeated_action_with_times_recorded__then_expected_call_count_is_taken_from_times_object(self):
        self.expect_foo().will_repeatedly(ActionStub(1)).times(5)
        assert self.uut.format_expected() == 'to be called 5 times'

    def test_if_expectation_has_one_single_and_one_repeated_actions_recorded__then_it_is_expected_to_be_called_at_least_once(self):
        self.expect_foo().\
            will_once(ActionStub(1)).\
            will_repeatedly(ActionStub(2))
        assert self.uut.format_expected() == 'to be called at least once'

    def test_if_expectation_has_one_single_and_one_repeated_action_with_times_two_recorded__then_it_is_expected_to_be_called_three_times(self):
        self.expect_foo().\
            will_once(ActionStub(1)).\
            will_repeatedly(ActionStub(2)).\
            times(2)
        assert self.uut.format_expected() == 'to be called 3 times'

    def test_if_expectation_has_one_single_and_one_repeated_action_with_times_at_least_two_recorded__then_it_is_expected_to_be_called_at_least_three_times(self):
        self.expect_foo().\
            will_once(ActionStub(1)).\
            will_repeatedly(ActionStub(2)).\
            times(AtLeast(2))
        assert self.uut.format_expected() == 'to be called at least 3 times'

    def test_if_expectation_has_one_single_and_one_repeated_action_with_times_at_most_two_recorded__then_it_is_expected_to_be_called_between_one_and_three_times(self):
        self.expect_foo().\
            will_once(ActionStub(1)).\
            will_repeatedly(ActionStub(2)).\
            times(AtMost(2))
        assert self.uut.format_expected() == 'to be called between 1 and 3 times'

    def test_if_expectation_has_one_single_and_one_repeated_action_with_times_between_one_and_two_recorded__then_it_is_expected_to_be_called_between_two_and_three_times(self):
        self.expect_foo().\
            will_once(ActionStub(1)).\
            will_repeatedly(ActionStub(2)).\
            times(Between(1, 2))
        assert self.uut.format_expected() == 'to be called between 2 and 3 times'


class TestFormatAction(TestBase):

    def test_if_no_actions_recorded__then_action_is_none(self):
        self.expect_foo()
        assert self.uut.format_action() is None

    def test_if_single_actions_recorded__then_formatted_action_is_a_next_action_to_execute(self):
        self.expect_foo().\
            will_once(ActionStub(1)).\
            will_once(ActionStub(2)).\
            will_once(ActionStub(3))
        assert self.uut.format_action() == 'ActionStub(1)'
        assert self.call_foo() == 1
        assert self.uut.format_action() == 'ActionStub(2)'
        assert self.call_foo() == 2
        assert self.uut.format_action() == 'ActionStub(3)'
        assert self.call_foo() == 3
        assert self.uut.format_action() is None

    def test_if_repeated_action_recorded__then_formatted_action_is_always_the_same(self):
        self.expect_foo().\
            will_repeatedly(ActionStub(1))
        assert self.uut.format_action() == 'ActionStub(1)'
        assert self.call_foo() == 1
        assert self.uut.format_action() == 'ActionStub(1)'

    def test_if_single_and_repeated_action_given__then_formatted_action_changes_accordingly(self):
        self.expect_foo().\
            will_once(ActionStub(1)).\
            will_once(ActionStub(2)).\
            will_repeatedly(ActionStub(3))
        assert self.uut.format_action() == 'ActionStub(1)'
        self.call_foo()
        assert self.uut.format_action() == 'ActionStub(2)'
        self.call_foo()
        assert self.uut.format_action() == 'ActionStub(3)'
        self.call_foo()
        assert self.uut.format_action() == 'ActionStub(3)'
