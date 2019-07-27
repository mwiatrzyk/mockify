# ---------------------------------------------------------------------------
# tests/test_matchers.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import pytest

from mockify.matchers import _


class TestAny:

    def test_string_representation(self):
        return repr(_) == '_'

    def test_any_matcher_is_equal_to_any_value(self):
        assert _ == 1
        assert _ == []
        assert _ == {}

    def test_checking_if_inequal_always_returns_false(self):
        assert not (_ != 1)
        assert not (_ != [])
        assert not (_ != {})

    def test_if_used_as_dict_value__then_that_dict_matches_another_dict_with_same_keys(self):
        assert {'a': _} == {'a': 123}
