import pytest

from mockify import exc, assert_satisfied, Call
from mockify.mock import FunctionMock
from mockify.actions import Return
from mockify.cardinality import AtMost

from tests.mixins import AssertUnsatisfiedAssertionMatchMixin


class TestFunctionMockBase(AssertUnsatisfiedAssertionMatchMixin):

    def setup_method(self):
        self.foo = FunctionMock('foo')


class TestSingleFunctionMock(TestFunctionMockBase):

    def test_when_no_expectations_and_no_calls__then_pass(self):
        self.foo.assert_satisfied()

    def test_when_one_expectation_and_one_matching_call__then_pass(self):
        self.foo.expect_call()
        self.foo()
        self.foo.assert_satisfied()

    def test_when_no_expectations_and_one_call__then_fail_on_call(self):
        with pytest.raises(exc.UninterestedCall) as excinfo:
            self.foo()
        assert excinfo.value.call == Call('foo')

    def test_when_one_expectation_and_non_matching_call__then_fail_on_call(self):
        self.foo.expect_call(1, 2)
        with pytest.raises(exc.UninterestedCall) as excinfo:
            self.foo()
        assert excinfo.value.call == Call('foo')

    def test_when_one_expectation_and_no_calls__then_fail(self):
        self.foo.expect_call()
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', None, 'to be called once', 'never called'))

    def test_when_two_different_expectations_and_no_calls__then_fail_with_two_never_called(self):
        self.foo.expect_call(1)
        self.foo.expect_call(2)
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo(1)', None, 'to be called once', 'never called'),
            ('foo(2)', None, 'to be called once', 'never called'))

    def test_when_two_different_expectations_and_only_one_matching_call__then_fail_with_never_called(self):
        self.foo.expect_call(1)
        self.foo.expect_call(2)
        self.foo(1)
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo(2)', None, 'to be called once', 'never called'))

    def test_when_one_expectation_and_two_calls__then_fail_with_too_many_calls(self):
        self.foo.expect_call(1)
        for _ in range(2):
            self.foo(1)
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo(1)', None, 'to be called once', 'called twice'))

    def test_when_two_expectations_and_two_calls_for_second__then_fail_with_second_expectation_having_too_many_calls(self):
        self.foo.expect_call(1)
        self.foo.expect_call(2)
        self.foo(1)
        for _ in range(2):
            self.foo(2)
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo(2)', None, 'to be called once', 'called twice'))

    def test_when_two_expectations_and_two_calls_for_first__then_fail_with_first_expectation_having_too_many_calls(self):
        self.foo.expect_call(1)
        self.foo.expect_call(2)
        for _ in range(2):
            self.foo(1)
        self.foo(2)
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo(1)', None, 'to be called once', 'called twice'))

    def test_when_same_expectation_given_twice_and_never_called__then_fail(self):
        self.foo.expect_call(1, 2)
        self.foo.expect_call(1, 2)
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo(1, 2)', None, 'to be called once', 'never called'),
            ('foo(1, 2)', None, 'to be called once', 'never called'))

    def test_when_same_expectation_given_twice_and_called_once__then_fail(self):
        self.foo.expect_call(1, 2)
        self.foo.expect_call(1, 2)
        self.foo(1, 2)
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo(1, 2)', None, 'to be called once', 'never called'))

    def test_when_same_expectation_given_twice_and_called_twice__then_pass(self):
        self.foo.expect_call(1, 2)
        self.foo.expect_call(1, 2)
        for _ in range(2):
            self.foo(1, 2)
        self.foo.assert_satisfied()

    def test_when_same_expectation_given_twice_and_called_three_times__then_fail(self):
        self.foo.expect_call(1, 2)
        self.foo.expect_call(1, 2)
        for _ in range(3):
            self.foo(1, 2)
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo(1, 2)', None, 'to be called once', 'called twice'))


class TestMultipleFunctionMocks(TestFunctionMockBase):

    def setup_method(self):
        self.foo = FunctionMock('foo')
        self.bar = FunctionMock('bar')

    ### Tests

    def test_expectations_can_be_resolved_in_any_order(self):
        self.foo.expect_call(1, 2, c=3)
        self.bar.expect_call('spam')
        with assert_satisfied(self.foo, self.bar):
            self.bar('spam')
            self.foo(1, 2, c=3)

    def test_when_two_expectations_and_only_one_satisfied__then_fail(self):
        self.foo.expect_call()
        self.bar.expect_call()
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            with assert_satisfied(self.foo, self.bar):
                self.foo()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('bar()', None, 'to be called once', 'never called'))


class TestExpectCallWithWillOnce(TestFunctionMockBase):

    def test_when_expected_to_once_return_value_and_called_once__then_call_returns_that_value(self):
        self.foo.expect_call().will_once(Return(1))
        assert self.foo() == 1
        self.foo.assert_satisfied()

    def test_when_expected_to_once_return_value_and_never_called__then_fail(self):
        self.foo.expect_call().will_once(Return(1))
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', 'Return(1)', 'to be called once', 'never called'))

    def test_when_expected_to_once_return_value_and_called_twice__then_fail(self):
        self.foo.expect_call().will_once(Return(1))
        for _ in range(2):
            assert self.foo() == 1
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', 'Return(1)', 'to be called once', 'called twice'))

    def test_when_expected_to_once_return_one_and_once_return_two_and_never_called__then_fail_with_error_pointing_to_first_action(self):
        self.foo.expect_call().will_once(Return(1)).will_once(Return(2))
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', 'Return(1)', 'to be called once', 'never called'))

    def test_when_expected_to_once_return_one_and_once_return_two_and_called_once__then_fail_with_error_pointing_to_second_action(self):
        self.foo.expect_call().will_once(Return(1)).will_once(Return(2))
        assert self.foo() == 1
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', 'Return(2)', 'to be called once', 'never called'))

    def test_when_expected_to_once_return_one_and_once_return_two_and_called_three_times__then_fail_with_error_pointing_to_second_action(self):
        self.foo.expect_call().will_once(Return(1)).will_once(Return(2))
        assert self.foo() == 1
        for _ in range(2):
            assert self.foo() == 2
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', 'Return(2)', 'to be called once', 'called twice'))

    def test_when_expected_to_once_return_one_and_once_return_two_and_called_twice__then_pass(self):
        self.foo.expect_call().will_once(Return(1)).will_once(Return(2))
        assert self.foo() == 1
        assert self.foo() == 2
        self.foo.assert_satisfied()


class TestExpectCallWithWillRepeatedly(TestFunctionMockBase):

    def test_when_expected_to_return_value_repeatedly_and_never_called__then_pass(self):
        self.foo.expect_call().will_repeatedly(Return(1))
        self.foo.assert_satisfied()

    def test_when_expected_to_return_value_repeatedly_and_called_once__then_pass_invoking_action(self):
        self.foo.expect_call().will_repeatedly(Return(1))
        assert self.foo() == 1
        self.foo.assert_satisfied()

    def test_when_expected_to_return_value_repeatedly_and_called_several_times__then_pass_each_time_invoking_action(self):
        self.foo.expect_call().will_repeatedly(Return(1))
        for _ in range(5):
            assert self.foo() == 1
        self.foo.assert_satisfied()

    ### .will_repeatedly(...).times(N)

    def test_when_expected_to_return_value_repeatedly_with_times_exactly_once_and_never_called__then_fail(self):
        self.foo.expect_call().will_repeatedly(Return(1)).times(1)
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', 'Return(1)', 'to be called once', 'never called'))

    def test_when_expected_to_return_value_repeatedly_with_times_exactly_once_and_called_twice__then_fail(self):
        self.foo.expect_call().will_repeatedly(Return(1)).times(1)
        for _ in range(2):
            assert self.foo() == 1
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', 'Return(1)', 'to be called once', 'called twice'))

    def test_when_expected_to_return_value_repeatedly_with_times_exactly_once_and_called_once__then_pass(self):
        self.foo.expect_call().will_repeatedly(Return(1)).times(1)
        assert self.foo() == 1
        self.foo.assert_satisfied()

    ### .will_repeatedly(...).times(AtMost(N))

    def when_when_expected_to_return_value_repeatedly_at_most_once_and_never_called__then_pass(self):
        self.foo.expect_call().will_repeatedly(Return(1)).times(AtMost(1))
        self.foo.assert_satisfied()

    def when_when_expected_to_return_value_repeatedly_at_most_once_and_called_once__then_pass(self):
        self.foo.expect_call().will_repeatedly(Return(1)).times(AtMost(1))
        assert self.foo() == 1
        self.foo.assert_satisfied()

    def test_when_expected_to_return_value_repeatedly_at_most_once_and_called_twice__then_fail(self):
        self.foo.expect_call().will_repeatedly(Return(1)).times(AtMost(1))
        for _ in range(2):
            assert self.foo() == 1
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', 'Return(1)', 'to be called at most once', 'called twice'))


class TestExpectCallWithWillOnceAndWillRepeatedly(TestFunctionMockBase):

    def test_when_expected_to_be_called_once_returning_one_and_then_repeatedly_returning_two_and_called_once__then_pass(self):
        self.foo.expect_call().\
            will_once(Return(1)).\
            will_repeatedly(Return(2))
        assert self.foo() == 1
        self.foo.assert_satisfied()

    def test_when_expected_to_be_called_once_returning_one_and_then_repeatedly_returning_two_and_called_twice__then_pass(self):
        self.foo.expect_call().\
            will_once(Return(1)).\
            will_repeatedly(Return(2))
        assert self.foo() == 1
        assert self.foo() == 2
        self.foo.assert_satisfied()

    def test_when_expected_to_be_called_once_returning_one_and_then_repeatedly_returning_two_and_called_three_times__then_pass(self):
        self.foo.expect_call().\
            will_once(Return(1)).\
            will_repeatedly(Return(2))
        assert self.foo() == 1
        for _ in range(2):
            assert self.foo() == 2
        self.foo.assert_satisfied()

    def test_when_expected_to_be_called_once_returning_one_and_then_repeatedly_returning_two_and_never_called__then_fail(self):
        self.foo.expect_call().\
            will_once(Return(1)).\
            will_repeatedly(Return(2))
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', 'Return(1)', 'to be called once', 'never called'))


class TestExpectCallWithWillOnceWillRepeatedlyAndTimes(TestFunctionMockBase):

    def test_when_expected_to_once_return_one_and_then_repeatedly_return_two_twice_and_never_called__then_fail(self):
        self.foo.expect_call().will_once(Return(1)).will_repeatedly(Return(2)).times(2)
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', 'Return(1)', 'to be called once', 'never called'))

    def test_when_expected_to_once_return_one_and_then_repeatedly_return_two_twice_and_called_once__then_fail(self):
        self.foo.expect_call().will_once(Return(1)).will_repeatedly(Return(2)).times(2)
        assert self.foo() == 1
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', 'Return(2)', 'to be called twice', 'never called'))

    def test_when_expected_to_once_return_one_and_then_repeatedly_return_two_twice_and_called_twice__then_fail(self):
        self.foo.expect_call().will_once(Return(1)).will_repeatedly(Return(2)).times(2)
        assert self.foo() == 1
        assert self.foo() == 2
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', 'Return(2)', 'to be called twice', 'called once'))

    def test_when_expected_to_once_return_one_and_then_repeatedly_return_two_twice_and_called_three_times__then_pass(self):
        self.foo.expect_call().will_once(Return(1)).will_repeatedly(Return(2)).times(2)
        assert self.foo() == 1
        for _ in range(2):
            assert self.foo() == 2
        self.foo.assert_satisfied()

    def test_when_expected_to_once_return_one_and_then_repeatedly_return_two_twice_and_called_four_times__then_fail(self):
        self.foo.expect_call().will_once(Return(1)).will_repeatedly(Return(2)).times(2)
        assert self.foo() == 1
        for _ in range(3):
            assert self.foo() == 2
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', 'Return(2)', 'to be called twice', 'called 3 times'))
