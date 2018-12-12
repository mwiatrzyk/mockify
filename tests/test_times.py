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

    def test_compare_with_actual_count(self):
        assert AtLeast(2) != 0
        assert AtLeast(2) != 1
        assert AtLeast(2) == 2
        assert AtLeast(2) == 3

    def test_format_expected(self):
        assert AtLeast(0).format_expected() is None  # any number of times
        assert AtLeast(1).format_expected() == 'to be called at least once'
        assert AtLeast(2).format_expected() == 'to be called at least twice'
        assert AtLeast(3).format_expected() == 'to be called at least 3 times'


class TestAtMost:

    def test_do_not_allow_maximal_count_less_than_zero(self):
        with pytest.raises(TypeError) as excinfo:
            uut = AtMost(-1)
        assert str(excinfo.value) == "value of 'maximal' must be >= 0"

    def test_at_most_zero_is_only_equal_to_zero_calls(self):
        assert AtMost(0) == 0
        assert AtMost(0) != 1


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
