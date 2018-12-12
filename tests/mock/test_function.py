# ---------------------------------------------------------------------------
# tests/mock/test_function_mock.py
#
# Copyright (C) 2018 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------

import collections

import pytest

from mockify import exc
from mockify.engine import Call, Registry
from mockify.mock.function import Function


ExpectationStub = collections.namedtuple('ExpectationStub', 'call, filename, lineno')


class RegistryStub:

    def __init__(self):
        self.call_params = []
        self.assert_unsatisfied_params = []
        self.assert_satisfied_params = []
        self.expectations = []

    def __call__(self, call):
        self.call_params.append(call)

    def expect_call(self, call, filename, lineno):
        expectation = ExpectationStub(call, filename, lineno)
        self.expectations.append(expectation)
        return expectation

    def assert_unsatisfied(self, name):
        self.assert_unsatisfied_params.append(name)

    def assert_satisfied(self, name):
        self.assert_satisfied_params.append(name)


class TestFunction:

    def setup_method(self):
        self.registry = RegistryStub()
        self.uut = Function('uut', registry=self.registry)

    def assert_registry_called_once(self, *args, **kwargs):
        assert len(self.registry.call_params) == 1
        assert self.registry.call_params[0].name == 'uut'
        assert self.registry.call_params[0].args == (args or None)
        assert self.registry.call_params[0].kwargs == (kwargs or None)

    def assert_registry_expectation_count_is(self, count):
        assert len(self.registry.expectations) == count

    def assert_registry_assert_unsatisfied_called_once(self):
        assert len(self.registry.assert_unsatisfied_params) == 1
        assert self.registry.assert_unsatisfied_params[0] == 'uut'

    def assert_registry_assert_satisfied_called_once(self):
        assert len(self.registry.assert_satisfied_params) == 1
        assert self.registry.assert_satisfied_params[0] == 'uut'

    ### Tests

    def test_when_called_without_args__then_registry_is_called_with_call_object_having_given_name_and_no_params(self):
        self.uut()
        self.assert_registry_called_once()

    def test_when_called_with_both_args_and_kwargs__then_registry_is_called_with_call_object_having_given_name_and_args_and_kwargs(self):
        self.uut(1, 2, c=3)
        self.assert_registry_called_once(1, 2, c=3)

    def test_when_expecting_to_be_called_without_params__then_registry_is_expected_to_be_called_with_call_object_having_given_name_and_no_params(self):
        expect = self.uut.expect_call()
        self.assert_registry_expectation_count_is(1)
        assert expect.call.name == 'uut'
        assert expect.call.args is None
        assert expect.call.kwargs is None
        assert expect.filename == __file__
        assert expect.lineno > 0

    def test_when_expecting_to_be_called_with_args_and_kwargs__then_registry_is_expected_to_be_called_with_call_object_having_given_name_and_args_and_kwargs(self):
        expect = self.uut.expect_call(1, 2, c=3)
        self.assert_registry_expectation_count_is(1)
        assert expect.call.name == 'uut'
        assert expect.call.args == (1, 2)
        assert expect.call.kwargs == {'c': 3}
        assert expect.filename == __file__
        assert expect.lineno > 0

    def test_when_assert_unsatisfied_is_called__then_registry_assert_unsatisfied_is_called_with_function_name(self):
        self.uut.assert_unsatisfied()
        self.assert_registry_assert_unsatisfied_called_once()

    def test_when_assert_sastisfied_is_called__then_registry_assert_satisfied_is_called_with_function_name(self):
        self.uut.assert_satisfied()
        self.assert_registry_assert_satisfied_called_once()
