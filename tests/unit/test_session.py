import pytest

from mockify import exc, Call, Session
from mockify.actions import Return


class TestContext:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.uut = Session()

    def test_newly_created_context_is_already_satisfied(self):
        self.uut.assert_satisfied()

    def test_if_expectation_is_recorded_and_consumed__then_context_is_satisfied(self):
        expected_call = Call('foo')
        self.uut.expect_call(expected_call).will_once(Return(123))
        assert self.uut(expected_call) == 123
        self.uut.assert_satisfied()

    def test_if_expectation_is_recorded_but_not_consumed__then_context_is_not_satisfied(self):
        expected_call = Call('foo')
        self.uut.expect_call(expected_call)
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.uut.assert_satisfied()
        e = excinfo.value
        assert len(e.expectations) == 1
        assert e.expectations[0].expected_call is expected_call

    def test_if_called_with_no_matching_expectation_recorded__then_raise_uninterested_call_error(self):
        actual_call = Call('foo')
        with pytest.raises(exc.UninterestedCall) as excinfo:
            self.uut(actual_call)
        e = excinfo.value
        assert e.call is actual_call

    def test_if_called_with_unexpected_params__then_raise_unexpected_call_error(self):
        actual_call = Call('foo')
        expected_call = Call('foo', 1, 2)
        self.uut.expect_call(expected_call)
        with pytest.raises(exc.UnexpectedCall) as excinfo:
            self.uut(actual_call)
        e = excinfo.value
        assert e.call is actual_call
        assert len(e.candidate_expectations) == 1
        assert e.candidate_expectations[0].expected_call is expected_call

    def test_if_expected_to_be_called_once_but_called_twice__then_context_is_not_satisfied(self):
        expected_call = Call('foo')
        self.uut.expect_call(expected_call).will_repeatedly(Return(123)).times(1)
        assert self.uut(expected_call) == 123
        assert self.uut(expected_call) == 123
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.uut.assert_satisfied()

    def test_if_two_expectations_recorded_and_both_called__then_context_is_satisfied(self):
        first_expected_call = Call('foo')
        second_expected_call = Call('bar')
        self.uut.expect_call(first_expected_call).will_once(Return(1))
        self.uut.expect_call(second_expected_call).will_once(Return(2))
        assert self.uut(first_expected_call) == 1
        assert self.uut(second_expected_call) == 2
        self.uut.assert_satisfied()

    def test_if_expectation_recorded_twice_but_called_once__then_context_is_not_satisfied(self):
        expected_call = Call('foo')
        self.uut.expect_call(expected_call).will_once(Return(1))
        self.uut.expect_call(expected_call).will_once(Return(2))
        assert self.uut(expected_call) == 1
        with pytest.raises(exc.Unsatisfied):
            self.uut.assert_satisfied()

    def test_if_expectation_recorded_twice_and_called_twice__then_context_is_satisfied(self):
        expected_call = Call('foo')
        self.uut.expect_call(expected_call).will_once(Return(1))
        self.uut.expect_call(expected_call).will_once(Return(2))
        assert self.uut(expected_call) == 1
        assert self.uut(expected_call) == 2
        self.uut.assert_satisfied()

    def test_if_uninterested_call_strategy_set_to_ignore__then_do_nothing_on_uninterested_calls(self):
        self.uut.uninterested_call_strategy = 'ignore'
        assert self.uut(Call('foo')) is None

    def test_if_uninterested_call_strategy_set_to_warn__then_issue_warning_on_uninterested_calls(self):
        self.uut.uninterested_call_strategy = 'warn'
        with pytest.warns(exc.UninterestedCallWarning, match='foo()'):
            assert self.uut(Call('foo')) is None

    def test_if_uninterested_call_strategy_set_to_an_invalid_value__then_issue_value_error(self):
        with pytest.raises(ValueError) as excinfo:
            self.uut.uninterested_call_strategy = 'dummy'
        assert str(excinfo.value) == "invalid strategy given: dummy"
