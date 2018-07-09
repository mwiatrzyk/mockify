import pytest

from mockify import Mock


class TestExpectCallWithoutArgs:

    def test_when_mock_called_with_no_expectations_set__then_fail_on_call(self):
        uut = Mock('uut')

        with pytest.raises(AssertionError) as excinfo:
            uut()

        assert str(excinfo.value) == "uninterested mock function called: uut()"

    def test_when_mock_called_once_with_expectation_set_once__then_pass(self):
        uut = Mock('uut')

        uut.expect_call()

        uut()

        uut.assert_satisfied()

    def test_when_mock_never_called_but_expectation_set_once__then_fail_on_assert_satisfied(self):
        uut = Mock('uut')

        uut.expect_call()

        with pytest.raises(AssertionError) as excinfo:
            uut.assert_satisfied()

        assert str(excinfo.value) == "mock function has unsatisfied expectations:\n"\
            "1. uut(): to be called once (expected), never called (actual)"
