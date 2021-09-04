# ---------------------------------------------------------------------------
# tests/unit/conftest.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import pytest

from mockify.abc import ICall


@pytest.fixture
def assert_that():
    """A placeholder for common helper assertions."""

    class AssertThat:

        @staticmethod
        def object_attr_match(obj, **attrs):
            for name, expected_value in attrs.items():
                assert getattr(obj, name) == expected_value

        @staticmethod
        def call_params_match(call: ICall, *expected_args, **expected_kwargs):
            assert call.args == expected_args
            assert call.kwargs == expected_kwargs

    return AssertThat
