import pytest

from mockify import exc
from mockify.engine import Call, Registry


class ExpectationStub:

    def __init__(self, expected_call, filename, lineno):
        self.expected_call = expected_call
        self.actual_calls = 0

    def __call__(self, call):
        self.actual_calls += 1

    def match(self, call):
        return self.expected_call == call

    def is_satisfied(self):
        return self.actual_calls == 1


class TestRegistry:

    def setup_method(self):
        self.foo_call = Call('foo')
        self.bar_call = Call('bar')
        self.uut = Registry(expectation_class=ExpectationStub)

    def expect_call_foo(self):
        return self.uut.expect_call(self.foo_call, 'foo.py', 123)

    def expect_call_bar(self):
        return self.uut.expect_call(self.bar_call, 'bar.py', 456)

    def call_foo(self):
        self.uut(self.foo_call)

    def call_bar(self):
        self.uut(self.bar_call)

    ### Tests

    def test_when_no_expectation_set__calling_fails_with_uninterested_call(self):
        with pytest.raises(exc.UninterestedCall) as excinfo:
            self.call_foo()
        assert excinfo.value.call is self.foo_call

    def test_assert_satisfied_can_be_called_with_mock_name_to_check_if_given_mock_is_satisfied(self):
        self.expect_call_foo()
        self.expect_call_bar()
        self.call_bar()
        with pytest.raises(exc.Unsatisfied):
            self.uut.assert_satisfied()
        self.uut.assert_satisfied('bar')
        self.call_foo()
        self.uut.assert_satisfied('foo')
        self.uut.assert_satisfied()

    def test_when_one_expectation_set__calling_with_same_params_passes(self):
        self.expect_call_foo()
        self.call_foo()
        self.uut.assert_satisfied()

    def test_when_one_expectation_set__calling_with_other_params_fails_with_uninterested_call(self):
        self.expect_call_foo()
        with pytest.raises(exc.UninterestedCall) as excinfo:
            self.call_bar()
        assert excinfo.value.call is self.bar_call

    def test_when_one_expectation_set__calling_with_same_params_twice_passes_but_registry_is_not_satisfied(self):
        foo_expect = self.expect_call_foo()
        self.call_foo()
        self.call_foo()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.uut.assert_satisfied()
        unsatisfied_expectations = excinfo.value.expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] is foo_expect

    def test_when_one_expectation_set_and_none_consumed__then_registry_is_not_satisfied(self):
        foo_expect = self.expect_call_foo()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.uut.assert_satisfied()
        unsatisfied_expectations = excinfo.value.expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] is foo_expect

    def test_when_two_different_expectations_set_and_both_consumed__then_registry_is_satisfied(self):
        self.expect_call_foo()
        self.expect_call_bar()
        self.call_foo()
        self.call_bar()
        self.uut.assert_satisfied()

    def test_when_two_different_expectations_set_and_one_consumed__then_registry_is_not_satisfied(self):
        self.expect_call_foo()
        bar_expect = self.expect_call_bar()
        self.call_foo()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.uut.assert_satisfied()
        unsatisfied_expectations = excinfo.value.expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] is bar_expect

    def test_when_two_same_expectations_set_and_consumed_twice__then_registry_is_satisfied(self):
        self.expect_call_foo()
        self.expect_call_foo()
        for _ in range(2):
            self.call_foo()
        self.uut.assert_satisfied()

    def test_when_two_same_expectations_set_and_consumed_once__then_second_expectation_is_not_satisfied(self):
        self.expect_call_foo()
        second_expect = self.expect_call_foo()
        self.call_foo()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.uut.assert_satisfied()
        unsatisfied_expectations = excinfo.value.expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] is second_expect

    def test_when_two_same_expectations_set_and_consumed_three_times__then_second_expectation_is_not_satisfied(self):
        self.expect_call_foo()
        second_expect = self.expect_call_foo()
        for _ in range(3):
            self.call_foo()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.uut.assert_satisfied()
        unsatisfied_expectations = excinfo.value.expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] is second_expect
