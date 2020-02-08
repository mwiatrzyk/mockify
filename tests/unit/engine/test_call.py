# ---------------------------------------------------------------------------
# tests/unit/engine/test_call.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import pytest

from inspect import currentframe, getframeinfo

from mockify import exc, Call, LocationInfo


class TestLocationInfo:

    def test_string_representation(self):
        uut = LocationInfo('foo.py', 123)
        assert str(uut) == 'foo.py:123'

    def test_access_filename_and_lineno(self):
        uut = LocationInfo('foo.py', 123)
        assert uut.filename == 'foo.py'
        assert uut.lineno == 123


class TestCall:

    def test_create_call_object_with_name_only(self):
        call = Call('foo')
        assert str(call) == 'foo()'
        assert repr(call) == "<mockify.Call('foo')>"
        assert call.name == 'foo'
        assert call.args == tuple()
        assert call.kwargs == {}

    def test_create_call_object_with_name_and_positional_args(self):
        call = Call('foo', 1, 'spam')
        assert str(call) == "foo(1, 'spam')"
        assert repr(call) == "<mockify.Call('foo', 1, 'spam')>"
        assert call.name == 'foo'
        assert call.args == (1, 'spam')
        assert call.kwargs == {}

    def test_create_call_object_with_name_and_with_both_positional_and_keyword_args(self):
        call = Call('foo', 1, 'spam', c=2, b=3)
        assert str(call) == "foo(1, 'spam', b=3, c=2)"
        assert repr(call) == "<mockify.Call('foo', 1, 'spam', b=3, c=2)>"
        assert call.name == 'foo'
        assert call.args == (1, 'spam')
        assert call.kwargs == {'c': 2, 'b': 3}

    @pytest.mark.parametrize('first, second', [
        (Call('foo'), Call('foo')),
        (Call('foo', 1, 2), Call('foo', 1, 2)),
        (Call('foo', 1, 2, c=3), Call('foo', 1, 2, c=3)),
    ])
    def test_two_call_objects_are_equal_if_names_and_params_are_equal(self, first, second):
        assert first == second

    @pytest.mark.parametrize('first, second', [
        (Call('foo'), Call('bar')),
        (Call('foo', 1, 2), Call('foo', 1, 3)),
        (Call('foo', 1, 2), Call('foo', 1, 2, 3)),
        (Call('foo', 1, 2, c=3), Call('foo', 1, 2, c=4)),
        (Call('foo', 1, 2, c=3), Call('foo', 1, 2, c=3, d=4)),
    ])
    def test_two_call_objects_are_not_equal_if_they_have_different_names_different_arg_values_or_different_args_count(self, first, second):
        assert first != second

    def test_call_location(self):
        call = Call('foo')
        frameinfo = getframeinfo(currentframe())
        assert call.location == LocationInfo(__file__, frameinfo.lineno - 1)

    @pytest.mark.parametrize('invalid_name', [
        '!@$asd', '123', '1abc', '', # Invalid identifier
        'for', 'while', 'if', 'def', 'with',  # Python keywords
        'foo..bar', '.foo.bar', 'foo.',  # Improper use of namespacing
        123, [], {}, None, # Non string values
    ])
    def test_name_must_be_a_valid_python_identifier(self, invalid_name):
        with pytest.raises(TypeError) as excinfo:
            call = Call(invalid_name)
        assert str(excinfo.value) == f"Mock name must be a valid Python identifier, got {invalid_name!r} instead"

    @pytest.mark.parametrize('namespaced_name', [
        'foo.bar',
        'foo.bar.baz',
        'foo.__call__',
        'foo.bar.baz.__spam'
    ])
    def test_call_can_be_created_with_name_composed_of_identifiers_glued_with_a_period(self, namespaced_name):
        call = Call(namespaced_name)
        assert call.name == namespaced_name
