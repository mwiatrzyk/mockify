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

import pytest

from mockify import exc
from mockify.mock import Function, Object
from mockify.actions import Return


class UUT(Object):
    __methods__ = ['foo', 'bar']
    __properties__ = ['spam']


class TestObject:

    def setup_method(self):
        self.uut = UUT('uut')

    ### Tests

    def test_when_object_is_constructed_directly__type_error_is_raised_due_to_lack_of_methods_and_or_property_names_definition_in_class(self):
        with pytest.raises(TypeError):
            obj = Object('obj')

    def test_when_accessing_attribute_that_is_neither_method_nor_property__then_attribute_error_is_raised(self):
        with pytest.raises(AttributeError) as excinfo:
            ret = self.uut.baz()

        assert str(excinfo.value) == "mock object 'uut' has no attribute named 'baz'"

    def test_when_invoking_a_method_with_unexpected_args__then_uninterested_call_exception_is_raised(self):
        with pytest.raises(exc.UninterestedCall) as excinfo:
            ret = self.uut.foo()

        assert excinfo.value.call.name == self.uut.foo.name

    def test_record_one_expectation_then_invoke_it_and_assert_that_object_is_satisfied(self):
        self.uut.expect_call('foo', 1, 2)
        self.uut.foo(1, 2)
        self.uut.assert_satisfied()

    def test_expect_method_to_be_called_twice_and_call_it_twice(self):
        self.uut.expect_call('foo', 1, 2).times(2)
        for _ in range(2):
            self.uut.foo(1, 2)
        self.uut.assert_satisfied()

    def test_when_two_method_call_expectations_recorded_and_only_one_satisfied__then_object_is_not_satisfied(self):
        self.uut.expect_call('foo', 1, 2)
        self.uut.expect_call('bar')
        self.uut.foo(1, 2)
        with pytest.raises(exc.Unsatisfied):
            self.uut.assert_satisfied()

    def test_when_two_method_call_expectations_recorded_and_both_call__then_object_mock_is_satisfied(self):
        self.uut.expect_call('foo')
        self.uut.expect_call('bar')
        self.uut.foo()
        self.uut.bar()
        self.uut.assert_satisfied()

    def test_when_property_set_while_no_expectations_are_recorded__then_fail_with_uninterested_call(self):
        with pytest.raises(exc.UninterestedSetterCall) as excinfo:
            self.uut.spam = 1

        assert str(excinfo.value) == 'uut.spam = 1'

    def test_when_setting_property_not_listed_in_properties_list__then_fail_with_attribute_error(self):
        with pytest.raises(AttributeError) as excinfo:
            self.uut.more_spam = 123

        assert str(excinfo.value) == "mock object 'uut' has no property 'more_spam'"

    def test_expect_property_to_be_set_once_and_set_it_once(self):
        self.uut.expect_set('spam', 1)
        self.uut.spam = 1
        self.uut.assert_satisfied()

    def test_expect_property_to_be_set_twice_and_set_it_twice(self):
        self.uut.expect_set('spam', 1).times(2)
        for _ in range(2):
            self.uut.spam = 1
        self.uut.assert_satisfied()

    def test_when_reading_property_with_no_read_expectations_set__then_fail_with_uninterested_call(self):
        with pytest.raises(exc.UninterestedGetterCall) as excinfo:
            spam = self.uut.spam
        assert str(excinfo.value) == 'uut.spam'

    def test_when_property_is_expected_to_be_read_once_and_it_is_read_once__then_object_is_satisfied(self):
        self.uut.expect_get('spam').will_once(Return(1))
        assert self.uut.spam == 1
        self.uut.assert_satisfied()

    def test_when_property_is_expected_to_be_read_and_write_once_and_it_is_not_written__then_object_is_not_satisfied(self):
        self.uut.expect_set('spam', 1)
        self.uut.expect_get('spam').will_once(Return(1))
        assert self.uut.spam == 1
        with pytest.raises(exc.Unsatisfied):
            self.uut.assert_satisfied()
