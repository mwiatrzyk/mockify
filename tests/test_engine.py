import pytest

from mockify import exc
from mockify.engine import StackInfo, Call, Registry, Expectation


class ActionStub:

    def __init__(self, return_value):
        self._return_value = return_value

    def __call__(self, call):
        return self._return_value


class TimesStub:

    def __eq__(self, actual):
        return actual >= 1


class TestRegistry:

    def make_foo_call(self):
        return Call('foo')

    def make_bar_call(self):
        return Call('bar')

    def setup_method(self):
        self.uut = Registry()

    ### Tests

    def test_when_no_expectation_set__calling_fails_with_uninterested_call(self):
        foo = self.make_foo_call()
        with pytest.raises(exc.UninterestedCall) as excinfo:
            self.uut(foo)
        assert excinfo.value.call is foo

    def test_when_one_expectation_set__calling_with_same_params_passes(self):
        foo = self.make_foo_call()
        self.uut.expect_call(foo)
        self.uut(foo)
        self.uut.assert_satisfied()

    def test_when_one_expectation_set__calling_with_other_params_fails_with_uninterested_call(self):
        foo = self.make_foo_call()
        bar = self.make_bar_call()
        self.uut.expect_call(foo)
        with pytest.raises(exc.UninterestedCall) as excinfo:
            self.uut(bar)
        assert excinfo.value.call is bar

    def test_when_one_expectation_set__calling_with_same_params_twice_passes_but_registry_is_not_satisfied(self):
        foo = self.make_foo_call()
        foo_expect = self.uut.expect_call(foo)
        self.uut(foo)
        self.uut(foo)
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.uut.assert_satisfied()
        unsatisfied_expectations = excinfo.value.unsatisfied_expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] is foo_expect

    def test_when_one_expectation_set_and_none_consumed__then_registry_is_not_satisfied(self):
        foo = self.make_foo_call()
        foo_expect = self.uut.expect_call(foo)
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.uut.assert_satisfied()
        unsatisfied_expectations = excinfo.value.unsatisfied_expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] is foo_expect

    def test_when_two_different_expectations_set_and_both_consumed__then_registry_is_satisfied(self):
        foo = self.make_foo_call()
        bar = self.make_bar_call()
        self.uut.expect_call(foo)
        self.uut.expect_call(bar)
        self.uut(foo)
        self.uut(bar)
        self.uut.assert_satisfied()

    def test_when_two_different_expectations_set_and_one_consumed__then_registry_is_not_satisfied(self):
        foo = self.make_foo_call()
        bar = self.make_bar_call()
        self.uut.expect_call(foo)
        bar_expect = self.uut.expect_call(bar)
        self.uut(foo)
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.uut.assert_satisfied()
        unsatisfied_expectations = excinfo.value.unsatisfied_expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] is bar_expect

    def test_when_two_same_expectations_set_and_consumed_twice__then_registry_is_satisfied(self):
        foo = self.make_foo_call()
        self.uut.expect_call(foo)
        self.uut.expect_call(foo)
        for _ in range(2):
            self.uut(foo)
        self.uut.assert_satisfied()

    def test_when_two_same_expectations_set_and_consumed_once__then_second_expectation_is_not_satisfied(self):
        foo = self.make_foo_call()
        self.uut.expect_call(foo)
        second_expect = self.uut.expect_call(foo)
        self.uut(foo)
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.uut.assert_satisfied()
        unsatisfied_expectations = excinfo.value.unsatisfied_expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] is second_expect

    def test_when_two_same_expectations_set_and_consumed_three_times__then_second_expectation_is_not_satisfied(self):
        foo = self.make_foo_call()
        self.uut.expect_call(foo)
        second_expect = self.uut.expect_call(foo)
        for _ in range(3):
            self.uut(foo)
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.uut.assert_satisfied()
        unsatisfied_expectations = excinfo.value.unsatisfied_expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] is second_expect


class TestExpectation:

    def setup_method(self):
        self.foo_call = Call('foo', stackinfo=StackInfo('foo.py', 123))
        self.bar_call = Call('bar', stackinfo=StackInfo('bar.py', 456))

    def expect_foo(self):
        self.uut = Expectation(self.foo_call)
        return self.uut

    def expect_bar(self):
        self.uut = Expectation(self.bar_call)
        return self.uut

    def call_bar(self):
        return self.uut(self.bar_call)

    def call_foo(self):
        return self.uut(self.foo_call)

    ### Tests

    def test_when_called_with_non_matching_call_object__then_raise_exception(self):
        self.expect_bar()
        with pytest.raises(TypeError):
            self.call_foo()

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

    def test_if_times_with_zero_value_called__it_is_expected_to_be_never_called(self):
        self.expect_foo().times(0)
        assert self.uut.is_satisfied()
        self.call_foo()
        assert not self.uut.is_satisfied()

    def test_if_times_with_times_object_called__it_is_expected_to_be_called_according_to_times_object_used(self):
        self.expect_foo().times(TimesStub())
        assert not self.uut.is_satisfied()
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
        for _ in range(2):
            assert self.call_foo() == 2
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
        assert self.call_foo() == 3
        assert not self.uut.is_satisfied()

    def test_expect_it_to_once_execute_given_action_and_then_execute_other_action_twice(self):
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
