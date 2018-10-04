import pytest

from mockify import exc, Context


class TestExpectCall:

    def setup_method(self):
        self.ctx = Context()
        self.mock = self.ctx.make_mock("mock")

    ### Tests

    def test_when_one_expect_call_and_one_mock_call__then_pass(self):
        self.mock.expect_call()
        self.mock()
        self.ctx.assert_satisfied()

    def test_when_one_expect_call_and_no_mock_calls__then_fail(self):
        self.mock.expect_call()
        with pytest.raises(exc.UnsatisfiedExpectationsError) as excinfo:
            self.ctx.assert_satisfied()
        assert str(excinfo.value) == "Following expectations were not satisfied:\n\t"\
            "#1. mock(): to be called once (expected) != never called (actual)"

    def test_when_one_expect_call_and_two_mock_calls__then_fail(self):
        self.mock.expect_call()
        self.mock()
        self.mock()
        with pytest.raises(exc.UnsatisfiedExpectationsError) as excinfo:
            self.ctx.assert_satisfied()
        assert str(excinfo.value) == "Following expectations were not satisfied:\n\t"\
            "#1. mock(): to be called once (expected) != called twice (actual)"

    def test_when_two_same_expect_calls_and_one_mock_call__then_fail(self):
        self.mock.expect_call()
        self.mock.expect_call()
        self.mock()
        with pytest.raises(exc.UnsatisfiedExpectationsError) as excinfo:
            self.ctx.assert_satisfied()
        assert str(excinfo.value) == "Following expectations were not satisfied:\n\t"\
            "#2. mock(): to be called once (expected) != never called (actual)"

    def test_when_three_different_expect_calls_and_only_one_mock_not_called__then_fail(self):
        self.mock.expect_call()
        self.mock.expect_call(1, 2, a="spam")
        self.mock.expect_call(1, 2)
        self.mock()
        self.mock(1, 2)
        with pytest.raises(exc.UnsatisfiedExpectationsError) as excinfo:
            self.ctx.assert_satisfied()
        assert str(excinfo.value) == "Following expectations were not satisfied:\n\t"\
            "#2. mock(1, 2, a='spam'): to be called once (expected) != never called (actual)"

    def test_when_expected_to_be_never_called_and_one_mock_call__then_fail(self):
        self.mock.expect_call().times(0)
        self.mock()
        with pytest.raises(exc.UnsatisfiedExpectationsError) as excinfo:
            self.ctx.assert_satisfied()
        assert str(excinfo.value) == "Following expectations were not satisfied:\n\t"\
            "#1. mock(): to be never called (expected) != called once (actual)"

    def test_when_mock_called_with_no_expectations_set__then_raise_exception(self):
        with pytest.raises(TypeError) as excinfo:
            self.mock()
        assert str(excinfo.value) == "Uninterested mock called: mock()"

    def test_when_expected_to_be_called_3_times_but_mock_called_4_times__then_fail(self):
        self.mock.expect_call().times(3)
        for _ in range(4):
            self.mock()
        with pytest.raises(exc.UnsatisfiedExpectationsError) as excinfo:
            self.ctx.assert_satisfied()
        assert str(excinfo.value) == "Following expectations were not satisfied:\n\t"\
            "#1. mock(): to be called 3 times (expected) != called 4 times (actual)"
