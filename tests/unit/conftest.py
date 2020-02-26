# ---------------------------------------------------------------------------
# tests/unit/conftest.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import pytest


@pytest.fixture
def assert_that():
    """A placeholder for common helper assertions."""

    class AssertThat:

        def object_attr_match(self, obj, **attrs):
            for name, expected_value in attrs.items():
                assert getattr(obj, name) == expected_value

    return AssertThat()
