import pytest

from mockify import exc, Context


class TestExpectCall:

    def test_when_one_expect_call_and_one_mock_call__then_pass(self):
        ctx = Context()
        mock = ctx.make_mock("mock")
        mock.expect_call()
        mock()
        ctx.assert_satisfied()

    def test_when_one_expect_call_and_no_mock_calls__then_fail(self):
        ctx = Context()
        mock = ctx.make_mock("mock")
        mock.expect_call()
        with pytest.raises(exc.UnsatisfiedExpectationsError) as excinfo:
            ctx.assert_satisfied()
        assert str(excinfo.value) == "Following expectations were not satisfied:\n\t"\
            "#1. mock(): to be called once (expected) != never called (actual)"

    def test_when_one_expect_call_and_two_mock_calls__then_fail(self):
        ctx = Context()
        mock = ctx.make_mock("mock")
        mock.expect_call()
        mock()
        mock()
        with pytest.raises(exc.UnsatisfiedExpectationsError) as excinfo:
            ctx.assert_satisfied()
        assert str(excinfo.value) == "Following expectations were not satisfied:\n\t"\
            "#1. mock(): to be called once (expected) != called twice (actual)"

    def test_when_two_same_expect_calls_and_one_mock_call__then_fail(self):
        ctx = Context()
        mock = ctx.make_mock("mock")
        mock.expect_call()
        mock.expect_call()
        mock()
        with pytest.raises(exc.UnsatisfiedExpectationsError) as excinfo:
            ctx.assert_satisfied()
        assert str(excinfo.value) == "Following expectations were not satisfied:\n\t"\
            "#2. mock(): to be called once (expected) != never called (actual)"

    def test_when_three_different_expect_calls_and_only_one_mock_not_called__then_fail(self):
        ctx = Context()
        mock = ctx.make_mock("mock")
        mock.expect_call()
        mock.expect_call(1, 2, a="spam")
        mock.expect_call(1, 2)
        mock()
        mock(1, 2)
        with pytest.raises(exc.UnsatisfiedExpectationsError) as excinfo:
            ctx.assert_satisfied()
        assert str(excinfo.value) == "Following expectations were not satisfied:\n\t"\
            "#2. mock(1, 2, a='spam'): to be called once (expected) != never called (actual)"

    def test_when_expected_to_be_never_called_and_one_mock_call__then_fail(self):
        ctx = Context()
        mock = ctx.make_mock("mock")
        mock.expect_call().times(0)
        mock()
        with pytest.raises(exc.UnsatisfiedExpectationsError) as excinfo:
            ctx.assert_satisfied()
        assert str(excinfo.value) == "Following expectations were not satisfied:\n\t"\
            "#1. mock(): to be never called (expected) != called once (actual)"

    def test_when_mock_called_with_no_expectations_set__then_raise_exception(self):
        ctx = Context()
        mock = ctx.make_mock("mock")
        with pytest.raises(TypeError) as excinfo:
            mock()
        assert str(excinfo.value) == "Uninterested mock called: mock()"

    def test_when_expected_to_be_called_3_times_but_mock_called_4_times__then_fail(self):
        ctx = Context()
        mock = ctx.make_mock("mock")
        mock.expect_call().times(3)
        for _ in range(4):
            mock()
        with pytest.raises(exc.UnsatisfiedExpectationsError) as excinfo:
            ctx.assert_satisfied()
        assert str(excinfo.value) == "Following expectations were not satisfied:\n\t"\
            "#1. mock(): to be called 3 times (expected) != called 4 times (actual)"
