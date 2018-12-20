# ---------------------------------------------------------------------------
# tests/test_cardinality.py
#
# Copyright (C) 2018 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------

import pytest

from mockify.times import AtLeast, AtMost, Between, Exactly


class TestExactly:

    def test_do_not_allow_exact_count_less_than_zero(self):
        with pytest.raises(TypeError) as excinfo:
            uut = Exactly(-1)
        assert str(excinfo.value) == "value of 'expected' must be >= 0"


class TestAtLeast:

    def test_do_not_allow_minimal_count_less_than_zero(self):
        with pytest.raises(TypeError) as excinfo:
            uut = AtLeast(-1)
        assert str(excinfo.value) == "value of 'minimal' must be >= 0"

    def test_at_least_with_zero_matches_any_number_of_calls(self):
        assert AtLeast(0) == 0
        assert AtLeast(0) == 1
        assert AtLeast(0) == 2

    def test_at_least_with_positive_value_matches_call_count_only_if_it_is_greater_or_equal(self):
        assert AtLeast(1) != 0
        assert AtLeast(1) == 1
        assert AtLeast(1) == 2

    def test_format_expected(self):
        assert AtLeast(0).format_expected() == 'to be called optionally'
        assert AtLeast(1).format_expected() == 'to be called at least once'
        assert AtLeast(2).format_expected() == 'to be called at least twice'
        assert AtLeast(3).format_expected() == 'to be called at least 3 times'


class TestAtMost:

    def test_do_not_allow_maximal_count_less_than_zero(self):
        with pytest.raises(TypeError) as excinfo:
            uut = AtMost(-1)
        assert str(excinfo.value) == "value of 'maximal' must be >= 0"

    def test_if_called_with_zero__then_exactly_with_zero_equivalent_is_creted(self):
        assert isinstance(AtMost(0), Exactly)

    def test_at_most_with_positive_value_matches_call_count_only_if_it_is_not_greater(self):
        assert AtMost(1) == 0
        assert AtMost(1) == 1
        assert AtMost(1) != 2

    def test_format_expected(self):
        assert AtMost(0).format_expected() == 'to be never called'
        assert AtMost(1).format_expected() == 'to be called at most once'
        assert AtMost(2).format_expected() == 'to be called at most twice'
        assert AtMost(3).format_expected() == 'to be called at most 3 times'


class TestBetween:

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

    def test_when_minimal_is_zero__then_at_most_is_created_instead(self):
        uut = Between(0, 1)
        assert isinstance(uut, AtMost)
        assert uut.format_expected() == 'to be called at most once'

    def test_between_with_range_matches_call_count_only_from_range(self):
        assert Between(1, 2) != 0
        assert Between(1, 2) == 1
        assert Between(1, 2) == 2
        assert Between(1, 2) != 3
