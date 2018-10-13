import pytest

from mockify import exc
from mockify.mock import FunctionMock
from mockify.cardinality import AtLeast, AtMost, Between, Exactly

from tests.mixins import AssertUnsatisfiedAssertionMatchMixin


class TestCardinality(AssertUnsatisfiedAssertionMatchMixin):

    def setup_method(self):
        self.foo = FunctionMock('foo')

    def run_fail_test_with_times(self, cardinality, calls, expected, actual):
        self.foo.expect_call().times(cardinality)
        for _ in range(calls):
            self.foo()
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', None, expected, actual))


class TestExactly(TestCardinality):

    def test_do_not_allow_exact_count_less_than_zero(self):
        with pytest.raises(TypeError) as excinfo:
            uut = Exactly(-1)
        assert str(excinfo.value) == "value of 'expected' must be >= 0"

    def test_when_expected_to_be_never_called_and_called_once__then_fail(self):
        self.run_fail_test_with_times(0, 1, 'to be never called', 'called once')

    def test_when_expected_to_be_called_twice_and_called_once__then_fail(self):
        self.run_fail_test_with_times(2, 1, 'to be called twice', 'called once')

    def test_when_expected_to_be_called_twice_and_called_three_times__then_fail(self):
        self.run_fail_test_with_times(2, 3, 'to be called twice', 'called 3 times')

    def test_when_expected_to_be_called_twice_and_called_twice__then_pass(self):
        self.foo.expect_call().times(2)
        for _ in range(2):
            self.foo()
        self.foo.assert_satisfied()


class TestAtLeast(TestCardinality):

    def test_do_not_allow_minimal_count_less_than_zero(self):
        with pytest.raises(TypeError) as excinfo:
            uut = AtLeast(-1)
        assert str(excinfo.value) == "value of 'minimal' must be >= 0"

    def test_when_expected_to_be_called_at_least_zero_times__then_pass_if_not_called(self):
        self.foo.expect_call().times(AtLeast(0))
        self.foo.assert_satisfied()

    def test_when_expected_to_be_called_at_least_zero_times__then_pass_if_called_one_or_more_times(self):
        self.foo.expect_call().times(AtLeast(0))
        self.foo()
        self.foo.assert_satisfied()
        for _ in range(3):
            self.foo()
        self.foo.assert_satisfied()

    def test_when_expected_to_be_called_at_least_once_and_never_called__then_fail(self):
        self.run_fail_test_with_times(AtLeast(1), 0, 'to be called at least once', 'never called')

    def test_when_expected_to_be_called_at_least_once_and_called_once__then_pass(self):
        self.foo.expect_call().times(AtLeast(1))
        self.foo()
        self.foo.assert_satisfied()

    def test_when_expected_to_be_called_at_least_once_and_called_twice__then_pass(self):
        self.foo.expect_call().times(AtLeast(1))
        for _ in range(2):
            self.foo()
        self.foo.assert_satisfied()


class TestAtMost(TestCardinality):

    def test_do_not_allow_maximal_count_less_than_zero(self):
        with pytest.raises(TypeError) as excinfo:
            uut = AtMost(-1)
        assert str(excinfo.value) == "value of 'maximal' must be >= 0"

    def test_when_expected_to_be_called_at_most_zero_times_and_never_called__then_pass(self):
        self.foo.expect_call().times(AtMost(0))
        self.foo.assert_satisfied()

    def test_when_expected_to_be_called_at_most_zero_times_and_called_once__then_fail(self):
        self.run_fail_test_with_times(AtMost(0), 1, 'to be never called', 'called once')

    def test_when_expected_to_be_called_at_most_once_and_never_called__then_pass(self):
        self.foo.expect_call().times(AtMost(1))
        self.foo.assert_satisfied()

    def test_when_expected_to_be_called_at_most_once_and_called_once__then_pass(self):
        self.foo.expect_call().times(AtMost(1))
        self.foo()
        self.foo.assert_satisfied()

    def test_when_expected_to_be_called_at_most_once_and_called_twice__then_fail(self):
        self.run_fail_test_with_times(AtMost(1), 2, 'to be called at most once', 'called twice')


class TestBetween(TestCardinality):

    def test_minimal_must_not_be_greater_than_maximal(self):
        with pytest.raises(TypeError) as excinfo:
            uut = Between(1, 0)
        assert str(excinfo.value) == "value of 'minimal' must not be greater than 'maximal'"

    def test_do_not_allow_minimal_count_less_than_zero(self):
        with pytest.raises(TypeError) as excinfo:
            uut = Between(-1, 0)
        assert str(excinfo.value) == "value of 'minimal' must be >= 0"

    def test_when_minimal_is_same_as_maximal__then_instance_of_exactly_object_is_created_instead(self):
        uut = Between(1, 1)
        assert isinstance(uut, Exactly)

    def test_when_expected_to_be_called_never_or_once_and_never_called__then_pass(self):
        self.foo.expect_call().times(Between(0, 1))
        self.foo.assert_satisfied()

    def test_when_expected_to_be_called_never_or_once_and_called_once__then_pass(self):
        self.foo.expect_call().times(Between(0, 1))
        self.foo()
        self.foo.assert_satisfied()

    def test_when_expected_to_be_called_once_or_twice_and_never_called__then_fail(self):
        self.run_fail_test_with_times(Between(1, 2), 0, 'to be called at least once but no more than twice', 'never called')

    def test_when_expected_to_be_called_once_or_twice_and_called_three_times__then_fail(self):
        self.run_fail_test_with_times(Between(1, 2), 3, 'to be called at least once but no more than twice', 'called 3 times')

    def test_when_expected_to_be_called_once_or_twice_and_called_once__then_pass(self):
        self.foo.expect_call().times(Between(1, 2))
        self.foo()
        self.foo.assert_satisfied()

    def test_when_expected_to_be_called_once_or_twice_and_called_twice__then_pass(self):
        self.foo.expect_call().times(Between(1, 2))
        for _ in range(2):
            self.foo()
        self.foo.assert_satisfied()
