# ---------------------------------------------------------------------------
# tests/unit/core/test_call.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
from inspect import currentframe, getframeinfo

import pytest

from mockify.core import Call, LocationInfo


class TestLocationInfo:

    def test_issue_deprecation_warning_if_location_info_is_used(self):
        with pytest.warns(DeprecationWarning) as rec:
            LocationInfo.get_external()
        assert len(rec) == 1
        first, = rec
        assert str(first.message) ==\
            "'mockify.core.LocationInfo' is deprecated since version (unreleased) "\
            "and will completely be removed in next major release."
        assert first.filename == __file__


class TestCall:

    def test_create_call_object_with_name_only(self):
        call = Call('foo')
        assert str(call) == 'foo()'
        assert repr(call) == "<mockify.core.Call('foo')>"
        assert call.name == 'foo'
        assert call.args == tuple()
        assert call.kwargs == {}

    def test_create_call_object_with_name_and_positional_args(self):
        call = Call('foo', 1, 'spam')
        assert str(call) == "foo(1, 'spam')"
        assert repr(call) == "<mockify.core.Call('foo', 1, 'spam')>"
        assert call.name == 'foo'
        assert call.args == (1, 'spam')
        assert call.kwargs == {}

    def test_create_call_object_with_name_and_with_both_positional_and_keyword_args(
        self
    ):
        call = Call('foo', 1, 'spam', c=2, b=3)
        assert str(call) == "foo(1, 'spam', b=3, c=2)"
        assert repr(call) == "<mockify.core.Call('foo', 1, 'spam', b=3, c=2)>"
        assert call.name == 'foo'
        assert call.args == (1, 'spam')
        assert call.kwargs == {'c': 2, 'b': 3}

    @pytest.mark.parametrize(
        'first, second', [
            (Call('foo'), Call('foo')),
            (Call('foo', 1, 2), Call('foo', 1, 2)),
            (Call('foo', 1, 2, c=3), Call('foo', 1, 2, c=3)),
        ]
    )
    def test_two_call_objects_are_equal_if_names_and_params_are_equal(
        self, first, second
    ):
        assert first == second

    @pytest.mark.parametrize(
        'first, second', [
            (Call('foo'), Call('bar')),
            (Call('foo', 1, 2), Call('foo', 1, 3)),
            (Call('foo', 1, 2), Call('foo', 1, 2, 3)),
            (Call('foo', 1, 2, c=3), Call('foo', 1, 2, c=4)),
            (Call('foo', 1, 2, c=3), Call('foo', 1, 2, c=3, d=4)),
        ]
    )
    def test_two_call_objects_are_not_equal_if_they_have_different_names_different_arg_values_or_different_args_count(
        self, first, second
    ):
        assert first != second

    def test_call_location(self):
        call = Call('foo')
        frameinfo = getframeinfo(currentframe())
        assert call.location.filename == __file__
        assert call.location.lineno == frameinfo.lineno - 1

    @pytest.mark.parametrize(
        'invalid_name',
        [
            '!@$asd',
            '123',
            '1abc',
            '',  # Invalid identifier
            'for',
            'while',
            'if',
            'def',
            'with',  # Python keywords
            'foo..bar',
            '.foo.bar',
            'foo.',  # Improper use of namespacing
            123,
            [],
            {},
            None,  # Non string values
        ]
    )
    def test_name_must_be_a_valid_python_identifier(self, invalid_name):
        with pytest.raises(TypeError) as excinfo:
            Call(invalid_name)
        assert str(
            excinfo.value
        ) == "Mock name must be a valid Python identifier, got {!r} instead".format(
            invalid_name
        )

    @pytest.mark.parametrize(
        'namespaced_name',
        ['foo.bar', 'foo.bar.baz', 'foo.__call__', 'foo.bar.baz.__spam']
    )
    def test_call_can_be_created_with_name_composed_of_identifiers_glued_with_a_period(
        self, namespaced_name
    ):
        call = Call(namespaced_name)
        assert call.name == namespaced_name
