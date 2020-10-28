# ---------------------------------------------------------------------------
# tests/unit/test_cardinality.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import pytest

from mockify import exc, satisfied
from mockify.actions import Return
from mockify.cardinality import (ActualCallCount, AtLeast, AtMost, Between,
                                 Exactly)
from mockify.mock import Mock


class TestActualCallCount:

    @pytest.mark.parametrize('value, message', [
        (0, 'never called'),
        (1, 'called once'),
        (2, 'called twice'),
        (3, 'called 3 times'),
        (4, 'called 4 times')
    ])
    def test_str(self, value, message):
        assert str(ActualCallCount(value)) == message

    def test_repr(self):
        assert repr(ActualCallCount(123)) == repr(123)


class TestExactly:

    def test_do_not_allow_exact_count_less_than_zero(self):
        with pytest.raises(TypeError) as excinfo:
            Exactly(-1)
        assert str(excinfo.value) == "value of 'expected' must be >= 0"

    @pytest.mark.parametrize('value, message', [
        (0, 'to be never called'),
        (1, 'to be called once'),
        (2, 'to be called twice'),
        (3, 'to be called 3 times'),
        (4, 'to be called 4 times')
    ])
    def test_str(self, value, message):
        assert str(Exactly(value)) == message

    def test_repr(self):
        assert repr(Exactly(2)) == "<mockify.cardinality.Exactly(2)>"

    def test_when_mock_expected_to_be_called_twice_but_was_called_once__then_mock_is_not_satisfied(self):
        mock = Mock('mock')
        mock.expect_call().times(2)
        with pytest.raises(exc.Unsatisfied) as excinfo:
            with satisfied(mock):
                mock()
        expectations = excinfo.value.unsatisfied_expectations
        assert len(expectations) == 1
        assert expectations[0].actual_call_count == 1
        assert expectations[0].expected_call_count == Exactly(2)

    def test_when_mock_expected_to_be_called_twice_and_was_called_twice__then_mock_is_satisfied(self):
        mock = Mock('mock')
        mock.expect_call().times(2)
        with satisfied(mock):
            for _ in range(2):
                mock()

    def test_when_mock_expected_to_be_called_twice_and_was_called_3_times__then_mock_is_not_satisfied(self):
        mock = Mock('mock')
        mock.expect_call().times(2)
        with pytest.raises(exc.Unsatisfied) as excinfo:
            with satisfied(mock):
                for _ in range(3):
                    mock()
        expectations = excinfo.value.unsatisfied_expectations
        assert len(expectations) == 1
        assert expectations[0].actual_call_count == 3
        assert expectations[0].expected_call_count == Exactly(2)

    def test_when_repeated_action_expected_to_be_called_twice_and_was_called_once__then_mock_is_not_satisfied(self):
        mock = Mock('mock')
        mock.expect_call().will_once(Return(1)).will_repeatedly(Return(2)).times(2)
        with pytest.raises(exc.Unsatisfied) as excinfo:
            with satisfied(mock):
                assert mock() == 1
                assert mock() == 2
        expectations = excinfo.value.unsatisfied_expectations
        assert len(expectations) == 1
        assert expectations[0].action == Return(2)
        assert expectations[0].actual_call_count == 2
        assert expectations[0].expected_call_count == Exactly(3)

    def test_when_repeated_action_expected_to_be_called_twice_and_was_called_three_times__then_mock_is_not_satisfied(self):
        mock = Mock('mock')
        mock.expect_call().will_once(Return(1)).will_repeatedly(Return(2)).times(2)
        with pytest.raises(exc.Unsatisfied) as excinfo:
            with satisfied(mock):
                assert mock() == 1
                for _ in range(3):
                    assert mock() == 2
        expectations = excinfo.value.unsatisfied_expectations
        assert len(expectations) == 1
        assert expectations[0].action == Return(2)
        assert expectations[0].actual_call_count == 4
        assert expectations[0].expected_call_count == Exactly(3)

    def test_when_repeated_action_expected_to_be_called_twice_and_was_called_twice__then_mock_is_satisfied(self):
        mock = Mock('mock')
        mock.expect_call().will_once(Return(1)).will_repeatedly(Return(2)).times(2)
        with satisfied(mock):
            assert mock() == 1
            for _ in range(2):
                assert mock() == 2


class TestAtLeast:

    def test_do_not_allow_minimal_count_less_than_zero(self):
        with pytest.raises(TypeError) as excinfo:
            AtLeast(-1)
        assert str(excinfo.value) == "value of 'minimal' must be >= 0"

    @pytest.mark.parametrize('value, message', [
        (0, 'to be called any number of times'),
        (1, 'to be called at least once'),
        (2, 'to be called at least twice'),
        (3, 'to be called at least 3 times'),
        (4, 'to be called at least 4 times')
    ])
    def test_str(self, value, message):
        assert str(AtLeast(value)) == message

    def test_repr(self):
        assert repr(AtLeast(2)) == "<mockify.cardinality.AtLeast(2)>"

    def test_when_mock_is_expected_to_be_called_at_least_once_and_was_never_called__then_mock_is_not_satisfied(self):
        mock = Mock('mock')
        mock.expect_call().times(AtLeast(1))
        with pytest.raises(exc.Unsatisfied) as excinfo:
            with satisfied(mock):
                pass
        expectations = excinfo.value.unsatisfied_expectations
        assert len(expectations) == 1
        assert expectations[0].actual_call_count == 0
        assert expectations[0].expected_call_count == AtLeast(1)

    def test_expect_mock_to_be_called_at_least_once_and_call_it_once(self):
        mock = Mock('mock')
        mock.expect_call().times(AtLeast(1))
        with satisfied(mock):
            mock()

    def test_expect_mock_to_be_called_at_least_once_and_call_it_twice(self):
        mock = Mock('mock')
        mock.expect_call().times(AtLeast(1))
        with satisfied(mock):
            for _ in range(2):
                mock()

    def test_when_repeated_action_expected_to_be_called_at_least_once_and_never_called__then_mock_is_not_satisfied(self):
        mock = Mock('mock')
        mock.expect_call().will_repeatedly(Return(1)).times(AtLeast(1))
        with pytest.raises(exc.Unsatisfied) as excinfo:
            with satisfied(mock):
                pass
        expectations = excinfo.value.unsatisfied_expectations
        assert len(expectations) == 1
        assert expectations[0].action == Return(1)
        assert expectations[0].actual_call_count == 0
        assert expectations[0].expected_call_count == AtLeast(1)

    def test_expect_repeated_action_to_be_called_at_least_once_and_call_it_once(self):
        mock = Mock('mock')
        mock.expect_call().will_repeatedly(Return(1)).times(AtLeast(1))
        with satisfied(mock):
            assert mock() == 1


class TestAtMost:

    def test_do_not_allow_maximal_count_less_than_zero(self):
        with pytest.raises(TypeError) as excinfo:
            AtMost(-1)
        assert str(excinfo.value) == "value of 'maximal' must be >= 0"

    def test_if_called_with_zero__then_exactly_with_zero_equivalent_is_created(self):
        assert isinstance(AtMost(0), Exactly)

    @pytest.mark.parametrize('value, message', [
        (0, 'to be never called'),
        (1, 'to be called at most once'),
        (2, 'to be called at most twice'),
        (3, 'to be called at most 3 times'),
        (4, 'to be called at most 4 times')
    ])
    def test_str(self, value, message):
        assert str(AtMost(value)) == message

    def test_repr(self):
        assert repr(AtMost(2)) == "<mockify.cardinality.AtMost(2)>"

    def test_when_mock_is_expected_to_be_called_at_most_twice_and_was_called_3_times__then_mock_is_not_satisfied(self):
        mock = Mock('mock')
        mock.expect_call().times(AtMost(2))
        with pytest.raises(exc.Unsatisfied) as excinfo:
            with satisfied(mock):
                for _ in range(3):
                    mock()
        expectations = excinfo.value.unsatisfied_expectations
        assert len(expectations) == 1
        assert expectations[0].actual_call_count == 3
        assert expectations[0].expected_call_count == AtMost(2)

    def test_expect_mock_to_be_called_at_most_once_and_call_it_once(self):
        mock = Mock('mock')
        mock.expect_call().times(AtMost(1))
        with satisfied(mock):
            mock()

    def test_expect_mock_to_be_called_at_most_once_and_never_call_it(self):
        mock = Mock('mock')
        mock.expect_call().times(AtMost(1))
        with satisfied(mock):
            pass


class TestBetween:

    def test_minimal_must_not_be_greater_than_maximal(self):
        with pytest.raises(TypeError) as excinfo:
            Between(1, 0)
        assert str(excinfo.value) == "value of 'minimal' must not be greater than 'maximal'"

    def test_do_not_allow_minimal_count_less_than_zero(self):
        with pytest.raises(TypeError) as excinfo:
            Between(-1, 0)
        assert str(excinfo.value) == "value of 'minimal' must be >= 0"

    def test_when_minimal_is_same_as_maximal__then_instance_of_exactly_object_is_created_instead(self):
        uut = Between(1, 1)
        assert isinstance(uut, Exactly)

    def test_when_minimal_is_zero__then_at_most_is_created_instead(self):
        uut = Between(0, 1)
        assert isinstance(uut, AtMost)

    @pytest.mark.parametrize('minimal, maximal, message', [
        (0, 1, 'to be called at most once'),
        (1, 2, 'to be called from 1 to 2 times'),
        (2, 2, 'to be called twice'),
    ])
    def test_str(self, minimal, maximal, message):
        assert str(Between(minimal, maximal)) == message

    def test_repr(self):
        assert repr(Between(1, 2)) == "<mockify.cardinality.Between(1, 2)>"

    def test_when_expected_to_be_called_1_to_2_times_and_never_called__then_mock_is_not_satisfied(self):
        mock = Mock('mock')
        mock.expect_call().times(Between(1, 2))
        with pytest.raises(exc.Unsatisfied) as excinfo:
            with satisfied(mock):
                pass
        expectations = excinfo.value.unsatisfied_expectations
        assert len(expectations) == 1
        assert expectations[0].actual_call_count == 0
        assert expectations[0].expected_call_count == Between(1, 2)

    def test_when_expected_to_be_called_1_to_2_times_and_called_3_times__then_mock_is_not_satisfied(self):
        mock = Mock('mock')
        mock.expect_call().times(Between(1, 2))
        with pytest.raises(exc.Unsatisfied) as excinfo:
            with satisfied(mock):
                for _ in range(3):
                    mock()
        expectations = excinfo.value.unsatisfied_expectations
        assert len(expectations) == 1
        assert expectations[0].actual_call_count == 3
        assert expectations[0].expected_call_count == Between(1, 2)

    def test_expect_mock_to_be_called_between_1_and_2_times_and_call_it_once(self):
        mock = Mock('mock')
        mock.expect_call().times(Between(1, 2))
        with satisfied(mock):
            mock()

    def test_expect_mock_to_be_called_between_1_and_2_times_and_call_it_twice(self):
        mock = Mock('mock')
        mock.expect_call().times(Between(1, 2))
        with satisfied(mock):
            for _ in range(2):
                mock()
