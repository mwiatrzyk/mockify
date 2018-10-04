import pytest

from mockify import exc, Context
from mockify.actions import Return, Raise, Invoke


class TestExpectCall:

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

    ### Tests

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
        self.mock(1, 2)
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock(1, 2, a='spam')", "to be called once", "never called")

    def test_when_expected_to_be_never_called_and_one_mock_call__then_fail(self):
        self.mock.expect_call().times(0)
        self.mock()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock()", "to be never called", "called once")

    def test_when_mock_called_with_no_expectations_set__then_raise_exception(self):
        with pytest.raises(TypeError) as excinfo:
            self.mock()
        assert str(excinfo.value) == "Uninterested mock called: mock()"

    def test_when_expected_to_be_called_3_times_but_mock_called_4_times__then_fail(self):
        self.mock.expect_call().times(3)
        for _ in range(4):
            self.mock()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        self.assert_unsatisfied_match(excinfo, "mock()", "to be called 3 times", "called 4 times")


class TestExpectCallOnceWithSideEffects:

    def setup_method(self):
        self.ctx = Context()
        self.mock = self.ctx.make_mock("mock")

    ### Tests

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
