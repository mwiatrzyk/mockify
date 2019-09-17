# ---------------------------------------------------------------------------
# tests/mock/test_object.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import sys
import math

from contextlib import contextmanager

import pytest

from _mockify import Call
from _mockify.mock import Object
from _mockify.actions import Return
from _mockify.matchers import _


class UUT(Object):
    __methods__ = ['foo', 'bar']
    __properties__ = ['spam']


class TestObjectSubclass:

    @pytest.fixture(autouse=True)
    def use_registry_mock(self, registry_mock):
        self.registry = registry_mock

    @pytest.fixture(autouse=True)
    def make_uut(self, use_registry_mock):
        self.uut = UUT('uut', registry=self.registry)

    ### Tests

    def test_when_accessing_attribute_that_is_neither_method_nor_property__then_attribute_error_is_raised(self):
        with pytest.raises(AttributeError) as excinfo:
            ret = self.uut.baz()

        assert str(excinfo.value) == "Mock object 'uut' has no attribute 'baz'"

    def test_record_method_call_expectation_using_old_interface(self):
        self.uut.expect_call('foo', 1, 2)
        assert self.registry.expected_calls == [Call('uut.foo', 1, 2)]

    def test_when_setting_property_not_listed_in_properties_list__then_fail_with_attribute_error(self):
        with pytest.raises(AttributeError) as excinfo:
            self.uut.more_spam = 123

        assert str(excinfo.value) == "Mock object 'uut' does not allow setting attribute 'more_spam'"

    def test_expect_property_set_using_old_interface(self):
        self.uut.expect_set('spam', 1)
        assert self.registry.expected_calls == [Call('uut.spam.fset', 1)]

    def test_when_property_get_using_old_interface(self):
        self.uut.expect_get('spam')
        assert self.registry.expected_calls == [Call('uut.spam.fget')]


class TestObject:

    @pytest.fixture(autouse=True)
    def use_registry_mock(self, registry_mock):
        self.registry = registry_mock

    @pytest.fixture(autouse=True)
    def make_uut(self, use_registry_mock):
        self.uut = Object('uut', registry=self.registry)

    @contextmanager
    def expect_uut_foo_fget(self, value):
        self.uut.foo.fget.expect_call()
        assert self.registry.expected_calls == [Call('uut.foo.fget')]
        self.registry.on_call = Return(value)
        yield self.uut.foo
        assert self.registry.calls == [Call('uut.foo.fget')]

    def test_when_getting_attribute__it_is_of_property_type_by_default(self):
        assert isinstance(self.uut.foo, Object.Property)

    def test_when_getting_fget_nested_attribute__it_is_of_getter_type(self):
        assert isinstance(self.uut.foo.fget, Object.Property.Getter)

    def test_when_getting_fset_nested_attribute__it_is_of_setter_type(self):
        assert isinstance(self.uut.foo.fset, Object.Property.Setter)

    def test_when_expect_call_is_called_on_property__then_it_becomes_a_method(self):
        self.uut.foo.expect_call()
        assert isinstance(self.uut.foo, Object.Method)
        assert self.registry.expected_calls == [Call('uut.foo')]

    def test_when_first_level_attribute_is_set__then_it_becomes_a_property(self):
        self.uut.foo = 123
        self.registry.on_call = Return(123)
        assert self.uut.foo == 123
        assert self.registry.calls == [Call('uut.foo.fset', 123), Call('uut.foo.fget')]

    def test_when_expect_call_is_called_on_fset__then_first_level_attribute_becomes_a_property(self):
        self.uut.foo.fset.expect_call(123)
        assert self.registry.expected_calls == [Call('uut.foo.fset', 123)]
        self.registry.on_call = Return(123)
        assert self.uut.foo == 123
        assert self.registry.calls == [Call('uut.foo.fget')]

    def test_when_expect_call_is_called_on_fget__then_first_level_attribute_becomes_a_property(self):
        self.uut.foo.fget.expect_call()
        assert self.registry.expected_calls == [Call('uut.foo.fget')]
        self.registry.on_call = Return(123)
        assert self.uut.foo == 123
        assert self.registry.calls == [Call('uut.foo.fget')]

    def test_when_fget_expectation_is_registered__then_getting_a_property_invokes_fget_mock(self):
        self.uut.foo.fget.expect_call()
        self.registry.expected_calls == [Call('uut.foo.fget')]
        self.registry.on_call = Return(123)
        assert self.uut.foo == 123
        self.registry.calls == [Call('uut.foo.fget')]

    def test_directly_calling_fset_is_not_allowed(self):
        with pytest.raises(TypeError) as excinfo:
            self.uut.foo.fset()
        assert str(excinfo.value) == "'Setter' object is not callable"

    def test_directly_calling_fget_is_not_allowed(self):
        with pytest.raises(TypeError) as excinfo:
            self.uut.foo.fget()
        assert str(excinfo.value) == "'Getter' object is not callable"

    def test_when_assert_satisfied_is_called__it_collects_all_mock_names_and_triggers_context(self):
        self.uut.foo.expect_call()
        self.uut.bar.fset.expect_call(123)
        self.uut.bar.fget.expect_call()
        self.uut.baz.fset.expect_call(456)
        assert self.registry.expected_calls == [
            Call('uut.foo'),
            Call('uut.bar.fset', 123),
            Call('uut.bar.fget'),
            Call('uut.baz.fset', 456)
        ]
        self.uut.assert_satisfied()
        assert self.registry.checked_mock_names == [
            'uut.foo', 'uut.bar.fset', 'uut.bar.fget', 'uut.baz.fset']

    def test_if_object_has_list_of_methods_defined__then_only_that_methods_are_allowed(self):
        self.uut = Object('uut', methods=('foo',), registry=self.registry)

        self.uut.foo.expect_call()
        assert self.registry.expected_calls == [Call('uut.foo')]

        with pytest.raises(AttributeError) as excinfo:
            self.uut.spam.expect_call()

        assert str(excinfo.value) == "Mock object 'uut' has no attribute 'spam'"

    def test_if_object_has_list_of_properties_defined__then_only_that_properties_are_allowed(self):
        self.uut = Object('uut', properties=('foo',), registry=self.registry)

        self.uut.foo.fset.expect_call(123)
        assert self.registry.expected_calls == [Call('uut.foo.fset', 123)]

        with pytest.raises(AttributeError) as excinfo:
            self.uut.bar.fset.expect_call(123)

        assert str(excinfo.value) == "Mock object 'uut' has no attribute 'bar'"

    def test_if_object_has_list_of_both_methods_and_properties_defined__then_you_cannot_use_method_as_property(self):
        self.uut = Object('uut', methods=('foo',), properties=('bar',), registry=self.registry)

        with pytest.raises(AttributeError) as excinfo:
            self.uut.foo.fset.expect_call(123)

        assert str(excinfo.value) == "'Method' object has no attribute 'fset'"

        with pytest.raises(AttributeError) as excinfo:
            self.uut.foo = 123

        assert str(excinfo.value) == "Mock object 'uut' does not allow setting attribute 'foo'"

    def test_if_property_is_accessed_twice__then_fget_is_called_twice(self):
        self.registry.on_call = Return(123)
        assert self.uut.foo == 123
        self.registry.on_call = Return(456)
        assert self.uut.foo == 456
        assert self.registry.calls == [Call('uut.foo.fget'), Call('uut.foo.fget')]

    def test_property_representation(self):
        with self.expect_uut_foo_fget('spam') as foo:
            assert repr(foo) == "'spam'"
            assert str(foo) == 'spam'

    def test_comparison_operators_on_property(self):
        with self.expect_uut_foo_fget(123) as foo:
            assert foo == 123
            assert foo != 124
            assert foo < 124
            assert foo <= 123
            assert foo > 122
            assert foo >= 123

    def test_unary_operations_on_property(self):
        with self.expect_uut_foo_fget(123) as foo:
            assert -foo == -123
            assert +foo == 123

    def test_abs_operation_on_property(self):
        with self.expect_uut_foo_fget(-123) as foo:
            assert abs(foo) == 123

    def test_invert_operation_on_property(self):
        with self.expect_uut_foo_fget(123) as foo:
            assert ~foo == -124

    def test_rounding_flooring_ceiling_and_truncating_float_property(self):
        with self.expect_uut_foo_fget(3.14) as foo:
            assert round(foo, 0) == 3
            assert math.floor(foo) == 3.0
            assert math.ceil(foo) == 4.0
            assert math.trunc(foo) == 3.0

    def test_arithmetic_operations_on_property(self):
        with self.expect_uut_foo_fget(2) as foo:
            assert foo + 3 == 5
            assert foo - 3 == -1
            assert foo * 3 == 6
            assert foo // 3 == 0
            assert foo / 4 == 0.5
            assert foo % 3 == 2
            assert divmod(foo, 3) == (0, 2)
            assert foo ** 2 == 4
            assert foo << 1 == 4
            assert foo >> 1 == 1
            assert foo & 3 == 2
            assert foo | 1 == 3
            assert foo ^ 3 == 1

    def test_reflected_arithmetic_operations_on_property(self):
        with self.expect_uut_foo_fget(2) as foo:
            assert 3 + foo == 5
            assert 3 - foo == 1
            assert 3 * foo == 6
            assert 3 // foo == 1
            assert 4 / foo == 2
            assert 3 % foo == 1
            assert divmod(3, foo) == (1, 1)
            assert 2 ** foo == 4
            assert 2 << foo == 8
            assert 2 >> foo == 0
            assert 3 & foo == 2
            assert 1 | foo == 3
            assert 3 ^ foo == 1

    def test_augumented_addition_on_property(self):
        with self.expect_uut_foo_fget(2) as foo:
            foo += 3
            assert foo == 5

    def test_augumented_subtraction_on_property(self):
        with self.expect_uut_foo_fget(2) as foo:
            foo -= 3
            assert foo == -1

    def test_augumented_multiplication_on_property(self):
        with self.expect_uut_foo_fget(2) as foo:
            foo *= 2
            assert foo == 4

    def test_augumented_floor_div_on_property(self):
        with self.expect_uut_foo_fget(2) as foo:
            foo //= 3
            assert foo == 0

    def test_augumented_div_on_property(self):
        with self.expect_uut_foo_fget(2) as foo:
            foo /= 4
            assert foo == 0.5

    def test_augumented_modulo_on_property(self):
        with self.expect_uut_foo_fget(2) as foo:
            foo %= 3
            assert foo == 2

    def test_augumented_pow_on_property(self):
        with self.expect_uut_foo_fget(2) as foo:
            foo **= 3
            assert foo == 8

    def test_augumented_lshift_on_property(self):
        with self.expect_uut_foo_fget(2) as foo:
            foo <<= 3
            assert foo == 16

    def test_augumented_rshift_on_property(self):
        with self.expect_uut_foo_fget(2) as foo:
            foo >>= 1
            assert foo == 1

    def test_augumented_and_on_property(self):
        with self.expect_uut_foo_fget(2) as foo:
            foo &= 3
            assert foo == 2

    def test_augumented_or_on_property(self):
        with self.expect_uut_foo_fget(2) as foo:
            foo |= 3
            assert foo == 3

    def test_augumented_xor_on_property(self):
        with self.expect_uut_foo_fget(2) as foo:
            foo ^= 3
            assert foo == 1

    def test_convert_property_to_int(self):
        with self.expect_uut_foo_fget(2.0) as foo:
            assert int(foo) == 2

    def test_convert_property_to_float(self):
        with self.expect_uut_foo_fget('3.14') as foo:
            assert float(foo) == 3.14

    def test_convert_property_to_complex(self):
        with self.expect_uut_foo_fget('3.14') as foo:
            assert complex(foo) == 3.14

    def test_format_property(self):
        with self.expect_uut_foo_fget('spam') as foo:
            assert f"{foo:s}" == 'spam'

    def test_calculate_hash_of_property(self):
        with self.expect_uut_foo_fget('spam') as foo:
            assert hash(foo) == hash('spam')

    def test_use_property_in_bool_expression(self):
        with self.expect_uut_foo_fget(0) as foo:
            assert not foo

    def test_dir_call_on_property(self):
        with self.expect_uut_foo_fget('spam') as foo:
            assert dir(foo) == dir('spam')

    def test_access_container_behind_a_property(self):
        with self.expect_uut_foo_fget({'a': 1, 'b': 2}) as foo:
            assert len(foo) == 2
            foo['a'] = 'spam'
            assert foo['a'] == 'spam'
            del foo['a']
            assert 'a' not in foo
            assert list(iter(foo)) == ['b']

    def test_get_attribute_of_value_behind_a_property(self):
        with self.expect_uut_foo_fget({'a': 1}) as foo:
            assert list(foo.keys()) == ['a']

    def test_call_a_function_assigned_to_property(self):
        with self.expect_uut_foo_fget(lambda: 123) as foo:
            assert foo() == 123
