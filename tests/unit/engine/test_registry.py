# ---------------------------------------------------------------------------
# tests/engine/test_registry.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import pytest

from _mockify import exc, Call, Registry


# class TestRegistry:

#     @pytest.fixture(autouse=True)
#     def setup(self, expectation_class_stub):
#         self.expectation_class = expectation_class_stub
#         self.uut = Registry(expectation_class=self.expectation_class)

#     def test_if_no_mocks_registered__then_registry_is_satisfied(self):
#         self.uut.assert_satisfied()

#     def test_register_namespace_in_registry(self):
#         foo = self.uut.add_namespace('foo')
#         assert foo.name == 'foo'

#     def test_registering_two_namespaces_of_same_name_is_not_allowed(self):
#         self.uut.add_namespace('foo')
#         with pytest.raises(ValueError) as excinfo:
#             self.uut.add_namespace('foo')
#         assert str(excinfo.value) == "Namespace 'foo' already exists"

#     @pytest.mark.parametrize('invalid_value', [
#         '!@$asd', '123', '1abc', # Invalid identifier
#         'for', 'while', 'if', 'def', 'with',  # Python keywords
#         123, [], # Non string values
#     ])
#     def test_registering_namespace_with_name_being_and_invalid_identifier_is_not_allowed(self, invalid_value):
#         with pytest.raises(ValueError) as excinfo:
#             self.uut.add_namespace(invalid_value)
#         assert str(excinfo.value) == f"Name {invalid_value!r} is not a valid identifier"

#     def test_registry_is_satisfied_if_it_has_namespaces_without_any_expectations_recorded(self):
#         self.uut.add_namespace('foo')
#         self.uut.add_namespace('bar')
#         self.uut.assert_satisfied()

#     def test_expect_mock_call_and_call_mock(self):
#         foo = self.uut.add_namespace('foo')
#         expectation = foo.expect_call('spam', 1, 2, c=3)
#         assert isinstance(expectation, self.expectation_class)
#         assert foo('spam', 1, 2, c=3) == self.expectation_class.return_value
#         self.uut.assert_satisfied()

#     def test_when_one_expectation_registered_but_not_consumed__then_assert_satisfied_fails(self):
#         foo = self.uut.add_namespace('foo')
#         expectation = foo.expect_call('spam', 1, 2, c=3)
#         with pytest.raises(exc.Unsatisfied) as excinfo:
#             self.uut.assert_satisfied()
#         assert excinfo.value.expectations == [expectation]



"""class ExpectationStub:

    def __init__(self, expected_call):
        self.expected_call = expected_call
        self.actual_calls = 0

    def __call__(self, call):
        self.actual_calls += 1

    def match(self, call):
        return self.expected_call == call

    def is_satisfied(self):
        return self.actual_calls == 1


class TestRegistry:

    def setup_method(self):
        self.foo_call = Call('foo')
        self.bar_call = Call('bar')
        self.uut = Registry(expectation_class=ExpectationStub)

    def expect_call_foo(self):
        return self.uut.expect_call(self.foo_call)

    def expect_call_bar(self):
        return self.uut.expect_call(self.bar_call)

    def call_foo(self):
        self.uut(self.foo_call)

    def call_bar(self):
        self.uut(self.bar_call)

    ### Tests

    def test_when_no_expectation_set__calling_fails_with_uninterested_call(self):
        with pytest.raises(exc.UninterestedCall) as excinfo:
            self.call_foo()
        assert excinfo.value.call is self.foo_call

    def test_assert_satisfied_can_be_called_with_mock_name_to_check_if_given_mock_is_satisfied(self):
        self.expect_call_foo()
        self.expect_call_bar()
        self.call_bar()
        with pytest.raises(exc.Unsatisfied):
            self.uut.assert_satisfied()
        self.uut.assert_satisfied('bar')
        self.call_foo()
        self.uut.assert_satisfied('foo')
        self.uut.assert_satisfied()

    def test_when_one_expectation_set__calling_with_same_params_passes(self):
        self.expect_call_foo()
        self.call_foo()
        self.uut.assert_satisfied()

    def test_when_one_expectation_set__calling_with_other_params_fails_with_uninterested_call(self):
        self.expect_call_foo()
        with pytest.raises(exc.UninterestedCall) as excinfo:
            self.call_bar()
        assert excinfo.value.call is self.bar_call

    def test_when_one_expectation_set__calling_with_same_params_twice_passes_but_registry_is_not_satisfied(self):
        foo_expect = self.expect_call_foo()
        self.call_foo()
        self.call_foo()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.uut.assert_satisfied()
        unsatisfied_expectations = excinfo.value.expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] is foo_expect

    def test_when_one_expectation_set_and_none_consumed__then_registry_is_not_satisfied(self):
        foo_expect = self.expect_call_foo()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.uut.assert_satisfied()
        unsatisfied_expectations = excinfo.value.expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] is foo_expect

    def test_when_two_different_expectations_set_and_both_consumed__then_registry_is_satisfied(self):
        self.expect_call_foo()
        self.expect_call_bar()
        self.call_foo()
        self.call_bar()
        self.uut.assert_satisfied()

    def test_when_two_different_expectations_set_and_one_consumed__then_registry_is_not_satisfied(self):
        self.expect_call_foo()
        bar_expect = self.expect_call_bar()
        self.call_foo()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.uut.assert_satisfied()
        unsatisfied_expectations = excinfo.value.expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] is bar_expect

    def test_when_two_same_expectations_set_and_consumed_twice__then_registry_is_satisfied(self):
        self.expect_call_foo()
        self.expect_call_foo()
        for _ in range(2):
            self.call_foo()
        self.uut.assert_satisfied()

    def test_when_two_same_expectations_set_and_consumed_once__then_second_expectation_is_not_satisfied(self):
        self.expect_call_foo()
        second_expect = self.expect_call_foo()
        self.call_foo()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.uut.assert_satisfied()
        unsatisfied_expectations = excinfo.value.expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] is second_expect

    def test_when_two_same_expectations_set_and_consumed_three_times__then_second_expectation_is_not_satisfied(self):
        self.expect_call_foo()
        second_expect = self.expect_call_foo()
        for _ in range(3):
            self.call_foo()
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.uut.assert_satisfied()
        unsatisfied_expectations = excinfo.value.expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] is second_expect
"""
