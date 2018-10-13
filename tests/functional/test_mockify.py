import pytest

from mockify import exc, Context
from mockify.actions import Return, Raise, Invoke
from mockify.matchers import _
from mockify.cardinality import AtLeast, AtMost, Between


class TestBase:

    def setup_method(self):
        self.ctx = Context()
        self.mock = self.ctx.make_mock("mock")

    def assert_unsatisfied_match(self, excinfo, mock, expected, actual):
        assert excinfo.match("at {}:\d+\n\t"
            "    Mock: {}\n\t"
            "Expected: {}\n\t"
            "  Actual: {}".format(
                __file__,
                mock.replace("(", "\(").replace(")", "\)"),
                expected, actual))


class TestExpectCall(TestBase):

    def test_when_one_expect_call_and_one_mock_call__then_pass(self):
        self.mock.expect_call()
        self.mock()
        self.ctx.assert_satisfied()

    def test_when_one_expect_call_and_no_mock_calls__then_fail(self):
        self.mock.expect_call()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock()", "to be called once", "never called")

    def test_when_one_expect_call_and_two_mock_calls__then_fail(self):
        self.mock.expect_call()
        self.mock()
        self.mock()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock()", "to be called once", "called twice")

    def test_when_two_same_expect_calls_and_one_mock_call__then_fail(self):
        self.mock.expect_call()
        self.mock.expect_call()
        self.mock()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock()", "to be called once", "never called")

    def test_when_three_different_expect_calls_and_only_one_mock_not_called__then_fail(self):
        self.mock.expect_call()
        self.mock.expect_call(1, 2, a="spam")
        self.mock.expect_call(1, 2)
        self.mock()
        self.mock(1, 2, a="spam")
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock(1, 2)", "to be called once", "never called")

    def test_when_expected_to_be_never_called_and_one_mock_call__then_fail(self):
        self.mock.expect_call().times(0)
        self.mock()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock()", "to be never called", "called once")

    def test_when_mock_called_with_no_expectations_set__then_raise_exception(self):
        with pytest.raises(exc.UninterestedMockCall) as excinfo:
            self.mock()
        assert str(excinfo.value) == "Uninterested mock call: mock()"

    def test_when_expected_to_be_called_3_times_but_mock_called_4_times__then_fail(self):
        self.mock.expect_call().times(3)
        for _ in range(4):
            self.mock()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock()", "to be called 3 times", "called 4 times")


class TestExpectCallWithSingleAction(TestBase):

    def test_when_expected_to_be_called_once_and_return_value__then_calling_a_mock_returns_that_value(self):
        self.mock.expect_call(1, 2).will_once(Return(3))
        assert self.mock(1, 2) == 3
        self.ctx.assert_satisfied()

    def test_when_expected_to_be_called_once_and_raise_exception__then_calling_a_mock_raises_that_exception(self):
        self.mock.expect_call(1, 2).will_once(Raise(RuntimeError("an error")))
        with pytest.raises(RuntimeError) as excinfo:
            self.mock(1, 2)
        assert str(excinfo.value) == "an error"
        self.ctx.assert_satisfied()

    def test_when_expected_to_be_called_once_and_invoke_function__then_calling_a_mock_invokes_that_function(self):

        def func(a, b, c=None):
            cache.append((a, b, c))
            return 123

        cache = []
        self.mock.expect_call(1, 2, c="spam").will_once(Invoke(func))
        assert self.mock(1, 2, c="spam") == 123
        assert cache == [(1, 2, "spam")]
        self.ctx.assert_satisfied()

    def test_when_will_once_set_twice_on_one_expectations__then_mock_must_be_executed_twice_each_time_returning_next_value_in_sequence(self):
        self.mock.expect_call().\
            will_once(Return("first")).\
            will_once(Return("second"))
        assert self.mock() == "first"
        assert self.mock() == "second"
        self.ctx.assert_satisfied()

    def test_when_will_once_set_twice_and_mock_called_once__then_fail(self):
        self.mock.expect_call().\
            will_once(Return(1)).\
            will_once(Return(2))
        assert self.mock() == 1
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock()", "to be called twice", "called once")


class TestExpectCallWithRepeatedAction(TestBase):

    def test_when_repeated_action_specified_and_no_cardinality__then_mock_can_be_executed_any_number_of_times(self):
        self.mock.expect_call().will_repeatedly(Return(123))
        self.ctx.assert_satisfied()
        assert self.mock() == 123
        assert self.mock() == 123
        self.ctx.assert_satisfied()

    def test_when_repeated_action_specified_to_be_executed_given_amount_of_times_and_actual_call_count_differs__then_fail(self):
        self.mock.expect_call().times(2).will_repeatedly(Return(123))
        self.mock()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock()", "to be called twice", "called once")


class TestExpectCallWithSingleAndRepeatedActionsSimultaneously(TestBase):

    def test_when_expectation_has_one_single_and_one_repeated_action__then_it_must_be_called_at_least_once(self):
        self.mock.expect_call().\
            will_once(Return(1)).\
            will_repeatedly(Return(2))
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock()", "to be called at least once", "never called")
        assert self.mock() == 1
        assert self.mock() == 2
        assert self.mock() == 2
        self.ctx.assert_satisfied()

    def test_when_expectation_has_one_single_and_one_repeated_action_with_cardinality__then_it_must_be_called_as_specified_by_cardinality(self):
        self.mock.expect_call().\
            will_once(Return(1)).\
            will_repeatedly(Return(2)).\
            times(3)
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock()", "to be called 3 times", "never called")
        assert self.mock() == 1
        assert self.mock() == 2
        assert self.mock() == 2
        self.ctx.assert_satisfied()
        assert self.mock() == 2
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock()", "to be called 3 times", "called 4 times")


class TestExpectCallWithCardinality(TestBase):

    def test_when_expected_to_be_called_at_least_twice_and_called_once__then_fail(self):
        self.mock.expect_call().times(AtLeast(2))
        self.mock()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock()", "to be called at least twice", "called once")

    def test_when_expected_to_be_called_at_most_twice_and_called_three_times__then_fail(self):
        self.mock.expect_call().times(AtMost(2))
        for _ in range(3):
            self.mock()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock()", "to be called at most twice", "called 3 times")

    def test_when_expected_to_be_called_at_least_twice_but_no_more_than_three_times_and_called_once__then_fail(self):
        self.mock.expect_call().times(Between(2, 3))
        self.mock()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock()", "to be called at least twice but no more than 3 times", "called once")

    def test_when_expected_to_be_called_at_least_twice_but_no_more_than_three_times_and_called_4_times__then_fail(self):
        self.mock.expect_call().times(Between(2, 3))
        for _ in range(4):
            self.mock()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock()", "to be called at least twice but no more than 3 times", "called 4 times")


class TestExpectCallWithAnyMatcher(TestBase):

    def test_when_expecting_to_be_called_with_any_argument_value__then_accept_any_argument(self):
        self.mock.expect_call(_).times(2)
        self.mock(1)
        self.mock(2)
        self.ctx.assert_satisfied()

    def test_when_called_with_different_number_of_args__then_fail(self):
        self.mock.expect_call(_, _)
        with pytest.raises(exc.UninterestedMockCall) as excinfo:
            self.mock(1, 2, 3)
        assert str(excinfo.value) == "Uninterested mock call: mock(1, 2, 3)"

    def test_expect_mock_to_be_called_twice_with_any_arg_and_then_one_more_time_with_given_arg(self):
        self.mock.expect_call(_).times(2)
        self.mock.expect_call("spam")
        self.mock(1)
        self.mock(2)
        self.mock("spam")
        self.ctx.assert_satisfied()

    def test_when_expecting_to_be_called_with_any_argument_but_never_called__then_fail(self):
        self.mock.expect_call(_)
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock(_)", "to be called once", "never called")


class TestExpectCallOrder(TestBase):

    def assert_unexpected_match(self, excinfo, expected, called):
        def fix(value):
            return value.replace("(", "\(").replace(")", "\)")
        assert excinfo.match("Unexpected mock called:\n\t"
            "Expected: {} \(at .+?:\d+\)\n\t"
            "  Actual: {}".format(fix(expected), fix(called)))

    ### Tests

    def test_by_default_expectations_must_be_fulfilled_in_order_defined_by_expect_calls(self):
        ctx = Context()
        mock = ctx.make_mock("mock")
        mock.expect_call(1)
        mock.expect_call(3)
        with pytest.raises(TypeError) as excinfo:
            mock(3)
        self.assert_unexpected_match(excinfo, "mock(1)", "mock(3)")

    def test_when_two_mocks_are_used__expectations_must_be_fulfilled_in_order_defined_by_expect_calls(self):
        ctx = Context()
        first, second = ctx.make_mocks("first", "second")
        second.expect_call()
        first.expect_call()
        with pytest.raises(TypeError) as excinfo:
            first()
        self.assert_unexpected_match(excinfo, "second()", "first()")

    def test_when_unordered_flag_is_set__then_expectations_can_be_resolved_in_any_order(self):
        ctx = Context(ordered=False)
        mock = ctx.make_mock("mock")
        mock.expect_call(3)
        mock.expect_call(1)
        mock.expect_call(2)
        mock(1)
        mock(3)
        mock(2)
        ctx.assert_satisfied()

    def test_with_unordered_flag_and_single_expectation__check_if_assertion_fails_when_mock_called_twice(self):
        ctx = Context(ordered=False)
        mock = ctx.make_mock("mock")
        mock.expect_call()
        mock()
        mock()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock()", "to be called once", "called twice")
