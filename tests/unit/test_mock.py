# ---------------------------------------------------------------------------
# tests/unit/test_mock.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import pytest

from mockify import exc, satisfied
from mockify.mock import Mock, MockFactory, MockInfo
from mockify.actions import Return


class TestMockFactory:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.uut = MockFactory()

    def test_mocks_created_by_factory_share_one_session_object(self):
        first = self.uut.mock('first')
        second = self.uut.mock('second')
        assert MockInfo(first).session  is MockInfo(second).session

    def test_created_mock_has_same_name_as_given_one(self):
        first = self.uut.mock('first')
        assert MockInfo(first).name == 'first'

    def test_when_factory_is_created_with_name__it_is_used_as_mock_name_prefix(self):
        self.uut = MockFactory('foo')
        first = self.uut.mock('first')
        assert MockInfo(first).name == 'foo.first'

    def test_mock_with_same_name_as_existing_mock_cannot_be_created(self):
        self.uut.mock('foo')
        with pytest.raises(TypeError) as excinfo:
            self.uut.mock('foo')
        assert str(excinfo.value) == "Name 'foo' is already in use"

    def test_create_nested_factory(self):
        nested = self.uut.factory('nested')
        first = nested.mock('first')
        assert MockInfo(first).name == 'nested.first'

    def test_mock_with_same_name_as_existing_factory_cannot_be_created(self):
        self.uut.factory('foo')
        with pytest.raises(TypeError) as excinfo:
            self.uut.mock('foo')
        assert str(excinfo.value) == "Name 'foo' is already in use"

    def test_factory_with_same_name_as_existing_factory_cannot_be_created(self):
        self.uut.factory('foo')
        with pytest.raises(TypeError) as excinfo:
            self.uut.factory('foo')
        assert str(excinfo.value) == "Name 'foo' is already in use"

    def test_factory_with_same_name_as_existing_mock_cannot_be_created(self):
        self.uut.mock('foo')
        with pytest.raises(TypeError) as excinfo:
            self.uut.factory('foo')
        assert str(excinfo.value) == "Name 'foo' is already in use"

    def test_create_mock_factory_with_custom_session_and_mock_class(self):

        def factory(name, session=None):
            return name, session

        self.uut = MockFactory(session='session', mock_class=factory)
        assert self.uut.mock('foo') == ('foo', 'session')

    def test_list_children(self):
        first = self.uut.mock('first')
        second = self.uut.factory('second')
        third = second.mock('third')
        assert list(x.mock for x in MockInfo(self.uut).children()) == [first, third]

    def test_list_expectations(self):
        first = self.uut.mock('first').expect_call()
        second = self.uut.factory('second')
        third = second.mock('third').expect_call()
        assert list(MockInfo(self.uut).expectations()) == [first, third]


class TestMock:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.uut = Mock('uut')

    def test_expect_mock_to_be_called_as_a_function_and_call_it(self):
        self.uut.expect_call(1, 2)
        with satisfied(self.uut):
            self.uut(1, 2)

    def test_expect_mock_property_to_be_called_as_a_method_and_call_it(self):
        self.uut.foo.expect_call(1)
        with satisfied(self.uut):
            self.uut.foo(1)

    def test_expect_two_mock_properties_to_be_called_as_a_method_and_call_them(self):
        self.uut.foo.expect_call(1)
        self.uut.bar.expect_call(2)
        with satisfied(self.uut):
            self.uut.foo(1)
            self.uut.bar(2)

    def test_expect_namespaced_property_to_be_called_as_a_method_and_call_it(self):
        self.uut.foo.bar.expect_call(1)
        with satisfied(self.uut):
            self.uut.foo.bar(1)

    def test_expect_double_namespaced_property_to_be_called_as_a_method_and_call_it(self):
        self.uut.foo.bar.baz.expect_call(1)
        with satisfied(self.uut):
            self.uut.foo.bar.baz(1)

    def test_expect_expect_call_to_be_called_and_call_it(self):
        self.uut.expect_call.expect_call(1)
        with satisfied(self.uut):
            self.uut.expect_call(1)

    def test_expect_namespaced_expect_call_to_be_called_and_call_it(self):
        self.uut.foo.expect_call.expect_call(1)
        with satisfied(self.uut):
            self.uut.foo.expect_call(1)

    def test_expect_property_get_and_get_it(self):
        self.uut.__getattr__.expect_call('foo').will_once(Return(1))
        with satisfied(self.uut):
            assert self.uut.foo == 1

    def test_when_property_already_exists__it_is_not_possible_to_record_get_expectation(self):
        _ = self.uut.foo
        with pytest.raises(TypeError) as excinfo:
            self.uut.__getattr__.expect_call('foo').will_once(Return(1))
        assert str(excinfo.value) ==\
            "__getattr__.expect_call() must be called with a non existing "\
            "property name, got 'foo' which already exists"

    def test_expect_namespaced_property_get_and_get_it(self):
        self.uut.foo.__getattr__.expect_call('bar').will_once(Return(1))
        with satisfied(self.uut):
            assert self.uut.foo.bar == 1

    def test_when_namespaced_property_already_exists__it_is_not_possible_to_record_get_expectation(self):
        _ = self.uut.foo.bar
        with pytest.raises(TypeError) as excinfo:
            self.uut.foo.__getattr__.expect_call('bar').will_once(Return(1))
        assert str(excinfo.value) ==\
            "__getattr__.expect_call() must be called with a non existing "\
            "property name, got 'bar' which already exists"

    def test_when_property_get_expectation_is_recorded_with_invalid_number_of_params__then_raise_type_error(self):
        with pytest.raises(TypeError) as excinfo:
            self.uut.__getattr__.expect_call('foo', 'bar')
        assert str(excinfo.value) == "expect_call() takes 2 positional arguments but 3 were given"

    @pytest.mark.parametrize('invalid_name', [
        '123',
        [],
        '@#$',
        '123foo'
    ])
    def test_when_property_get_expectation_is_recorded_with_invalid_property_name__then_raise_type_error(self, invalid_name):
        with pytest.raises(TypeError) as excinfo:
            self.uut.__getattr__.expect_call(invalid_name)
        assert str(excinfo.value) ==\
            f"__getattr__.expect_call() must be called with valid Python property name, got {invalid_name!r}"

    def test_when_property_is_expected_to_be_get_and_is_never_get__then_raise_unsatisfied_error(self):
        expectation = self.uut.__getattr__.expect_call('spam')
        with pytest.raises(exc.Unsatisfied) as excinfo:
            with satisfied(self.uut):
                pass
        unsatisfied_expectations = excinfo.value.unsatisfied_expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] == expectation

    def test_when_property_is_set__getting_it_returns_same_value(self):
        self.uut.foo = 123
        assert self.uut.foo == 123

    def test_when_namespaced_property_is_set__getting_it_returns_same_value(self):
        self.uut.foo.bar = 123
        assert self.uut.foo.bar == 123

    def test_expect_property_to_be_set_and_set_it(self):
        self.uut.__setattr__.expect_call('foo', 123)
        with satisfied(self.uut):
            self.uut.foo = 123

    def test_when_property_already_exists__it_is_not_possible_to_record_set_expectation(self):
        self.uut.foo = 1
        with pytest.raises(TypeError) as excinfo:
            self.uut.__setattr__.expect_call('foo', 2)
        assert str(excinfo.value) ==\
            "__setattr__.expect_call() must be called with a non existing "\
            "property name, got 'foo' which already exists"

    def test_when_property_set_expectation_is_recorded_with_invalid_number_of_params__then_raise_type_error(self):
        with pytest.raises(TypeError) as excinfo:
            self.uut.__setattr__.expect_call('foo', 'bar', 'baz')
        assert str(excinfo.value) == "expect_call() takes 3 positional arguments but 4 were given"

    @pytest.mark.parametrize('invalid_name', [
        '123',
        [],
        '@#$',
        '123foo'
    ])
    def test_when_property_set_expectation_is_recorded_with_invalid_property_name__then_raise_type_error(self, invalid_name):
        with pytest.raises(TypeError) as excinfo:
            self.uut.__setattr__.expect_call(invalid_name, 123)
        assert str(excinfo.value) ==\
            f"__setattr__.expect_call() must be called with valid Python property name, got {invalid_name!r}"

    def test_when_property_is_expected_to_be_set_and_is_never_set__then_raise_unsatisfied_error(self):
        expectation = self.uut.__setattr__.expect_call('spam', 123)
        with pytest.raises(exc.Unsatisfied) as excinfo:
            with satisfied(self.uut):
                pass
        unsatisfied_expectations = excinfo.value.unsatisfied_expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] == expectation

    def test_record_set_and_get_expectations_for_same_property(self):
        self.uut.__setattr__.expect_call('foo', 123)
        self.uut.__getattr__.expect_call('foo').will_once(Return(123))
        with satisfied(self.uut):
            self.uut.foo = 123
            assert self.uut.foo == 123

    def test_when_action_chain_is_recorded__invoking_mock_consumes_actions_one_by_one(self):
        self.uut.expect_call().\
            will_once(Return(1)).\
            will_once(Return(2)).\
            will_once(Return(3))
        with satisfied(self.uut):
            assert [self.uut() for _ in range(3)] == [1, 2, 3]
