# ---------------------------------------------------------------------------
# tests/unit/core/test_session.py
#
# Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import pytest

from mockify import exc
from mockify.core import Call, Session
from mockify.actions import Return
from mockify.cardinality import Exactly


class TestContext:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.uut = Session()

    def test_newly_created_session_does_not_throw_unsatisfied_when_done_is_called(
        self
    ):
        self.uut.assert_satisfied()

    def test_if_expectation_is_recorded_and_consumed__then_session_is_satisfied(
        self
    ):
        expected_call = Call('foo')
        self.uut.expect_call(expected_call).will_once(Return(123))
        assert self.uut(expected_call) == 123
        self.uut.assert_satisfied()

    def test_if_expectation_is_recorded_but_not_consumed__then_session_is_not_satisfied(
        self, assert_that
    ):
        expected_call = Call('foo')
        self.uut.expect_call(expected_call)
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.uut.assert_satisfied()
        expectations = excinfo.value.unsatisfied_expectations
        assert len(expectations) == 1
        assert_that.object_attr_match(
            expectations[0],
            expected_call=expected_call,
            actual_call_count=0,
            expected_call_count=Exactly(1)
        )

    def test_if_called_with_no_matching_expectation_recorded__then_raise_uninterested_call_error(
        self
    ):
        actual_call = Call('foo')
        with pytest.raises(exc.UninterestedCall) as excinfo:
            self.uut(actual_call)
        value = excinfo.value
        assert value.actual_call == actual_call

    def test_if_called_with_unexpected_params__then_raise_unexpected_call_error(
        self
    ):
        actual_call = Call('foo')
        expected_call = Call('foo', 1, 2)
        self.uut.expect_call(expected_call)
        with pytest.raises(exc.UnexpectedCall) as excinfo:
            self.uut(actual_call)
        value = excinfo.value
        assert value.actual_call == actual_call
        assert len(value.expected_calls) == 1
        assert value.expected_calls[0] == expected_call

    def test_if_expected_to_be_called_once_but_called_twice__then_session_is_not_satisfied(
        self, assert_that
    ):
        expected_call = Call('foo')
        self.uut.expect_call(expected_call).will_repeatedly(Return(123)
                                                            ).times(1)
        assert self.uut(expected_call) == 123
        assert self.uut(expected_call) == 123
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.uut.assert_satisfied()
        expectations = excinfo.value.unsatisfied_expectations
        assert len(expectations) == 1
        assert_that.object_attr_match(
            expectations[0],
            expected_call=expected_call,
            actual_call_count=2,
            expected_call_count=Exactly(1)
        )

    def test_if_two_expectations_recorded_and_both_called__then_context_is_satisfied(
        self
    ):
        first_expected_call = Call('foo')
        second_expected_call = Call('bar')
        self.uut.expect_call(first_expected_call).will_once(Return(1))
        self.uut.expect_call(second_expected_call).will_once(Return(2))
        assert self.uut(first_expected_call) == 1
        assert self.uut(second_expected_call) == 2
        self.uut.assert_satisfied()

    def test_if_expectation_recorded_twice_but_called_once__then_context_is_not_satisfied(
        self, assert_that
    ):
        expected_call = Call('foo')
        self.uut.expect_call(expected_call).will_once(Return(1))
        self.uut.expect_call(expected_call).will_once(Return(2))
        assert self.uut(expected_call) == 1
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.uut.assert_satisfied()
        expectations = excinfo.value.unsatisfied_expectations
        assert len(expectations) == 1
        assert_that.object_attr_match(
            expectations[0],
            expected_call=expected_call,
            actual_call_count=0,
            expected_call_count=Exactly(1),
            action=Return(2)
        )

    def test_if_expectation_recorded_twice_and_called_twice__then_context_is_satisfied(
        self
    ):
        expected_call = Call('foo')
        self.uut.expect_call(expected_call).will_once(Return(1))
        self.uut.expect_call(expected_call).will_once(Return(2))
        assert self.uut(expected_call) == 1
        assert self.uut(expected_call) == 2
        self.uut.assert_satisfied()

    def test_if_uninterested_call_strategy_set_to_ignore__then_do_nothing_on_uninterested_calls(
        self
    ):
        self.uut.config['uninterested_call_strategy'] = 'ignore'
        assert self.uut(Call('foo')) is None

    def test_if_uninterested_call_strategy_set_to_warn__then_issue_warning_on_uninterested_calls(
        self
    ):
        self.uut.config['uninterested_call_strategy'] = 'warn'
        with pytest.warns(exc.UninterestedCallWarning, match='foo()'):
            assert self.uut(Call('foo')) is None

    def test_if_uninterested_call_strategy_set_to_an_invalid_value__then_issue_value_error(
        self
    ):
        with pytest.raises(ValueError) as excinfo:
            self.uut.config['uninterested_call_strategy'] = 'dummy'
        assert str(excinfo.value) ==\
            "Invalid value for 'uninterested_call_strategy' config option given: "\
            "expected any of ('fail', 'warn', 'ignore'), got 'dummy'"

    def test_when_ordered_mocks_are_called_in_invalid_order__then_fail_with_unexpected_call_order_error(
        self
    ):
        first = Call('first')
        second = Call('second')
        self.uut.expect_call(first)
        self.uut.expect_call(second)
        with pytest.raises(exc.UnexpectedCallOrder) as excinfo:
            self.uut.enable_ordered([first.name, second.name])
            self.uut(second)
        value = excinfo.value
        assert value.actual_call == second
        assert value.expected_call == first

    def test_non_consumed_ordered_expectations_are_made_unordered_again_when_disable_ordered_is_called(
        self
    ):
        first = Call('first')
        first_expectation = self.uut.expect_call(first)
        self.uut.enable_ordered([first.name])
        self.uut.disable_ordered()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.uut.assert_satisfied()
        assert len(excinfo.value.unsatisfied_expectations) == 1
        assert excinfo.value.unsatisfied_expectations[0] == first_expectation
