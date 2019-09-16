# ---------------------------------------------------------------------------
# tests/mock/test_module.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------
import pytest

from _mockify import exc
from _mockify.mock import Namespace, Function


class TestNamespace:

    def test_getting_attributes_returns_submodules(self):
        uut = Namespace('uut')

        assert uut.foo.name == 'uut.foo'
        assert uut.foo.bar.baz.name == 'uut.foo.bar.baz'

    def test_when_expect_call_is_called_on_first_level_submodule__it_replaces_it_with_a_default_mock(self):
        uut = Namespace('uut', mock_class=Function)

        assert not isinstance(uut.foo, Function)

        uut.foo.expect_call()

        assert isinstance(uut.foo, Function)
        assert uut.foo.name == 'uut.foo'

    def test_when_expect_call_is_called_on_nth_level_submodule__it_replaces_it_with_a_default_mock(self):
        uut = Namespace('uut', mock_class=Function)

        assert not isinstance(uut.foo, Function)
        assert not isinstance(uut.foo.bar, Function)
        assert not isinstance(uut.foo.bar.baz, Function)

        uut.foo.bar.baz.expect_call()

        assert not isinstance(uut.foo, Function)
        assert not isinstance(uut.foo.bar, Function)
        assert isinstance(uut.foo.bar.baz, Function)
        assert uut.foo.bar.baz.name == 'uut.foo.bar.baz'

    def test_when_module_is_called_without_expectation_set__then_raise_uninterested_call_error(self):
        uut = Namespace('uut')

        with pytest.raises(exc.UninterestedCall) as excinfo:
            uut.foo.bar.dummy_function(1, 2, c=3)

        assert str(excinfo.value) == 'uut.foo.bar.dummy_function(1, 2, c=3)'

    def test_register_and_resolve_one_expectation(self):
        uut = Namespace('uut')

        uut.foo.bar.dummy_function.expect_call(1, 2, c=3)

        uut.foo.bar.dummy_function(1, 2, c=3)

        uut.assert_satisfied()

    def test_register_and_resolve_two_expectations_on_two_different_mocks(self):
        uut = Namespace('uut')

        uut.foo.bar.first.expect_call(1)
        uut.foo.baz.spam.second.expect_call(2)

        uut.foo.bar.first(1)
        uut.foo.baz.spam.second(2)

        uut.assert_satisfied()

    def test_once_mock_is_registered__you_cannot_record_expectations_on_contained_paths(self):
        uut = Namespace('uut')

        uut.foo.bar.first.expect_call(1)

        with pytest.raises(TypeError) as excinfo:
            uut.foo.expect_call(2)

        assert str(excinfo.value) == (
            "Cannot record expectation: 'uut.foo' is a subpath of another "
            "mock 'uut.foo.bar.first' registered earlier."
        )
