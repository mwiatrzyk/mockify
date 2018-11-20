# ---------------------------------------------------------------------------
# tests/test_actions.py
#
# Copyright (C) 2018 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------

import pytest

from mockify import exc
from mockify.mock import FunctionMock
from mockify.actions import Raise, Invoke

from tests.mixins import AssertUnsatisfiedAssertionMatchMixin


class TestActionsBase(AssertUnsatisfiedAssertionMatchMixin):

    def setup_method(self):
        self.foo = FunctionMock('foo')


class TestRaise(TestActionsBase):

    def test_when_expected_to_once_raise_exception_and_never_called__then_fail(self):
        self.foo.expect_call().will_once(Raise(Exception('an error')))
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', "Raise(Exception('an error',))", 'to be called once', 'never called'))

    def test_when_expected_to_once_raise_exception_and_called_twice__then_fail(self):
        self.foo.expect_call().will_once(Raise(Exception('an error')))
        for _ in range(2):
            with pytest.raises(Exception) as excinfo:
                self.foo()
            assert str(excinfo.value) == 'an error'
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', "Raise(Exception('an error',))", 'to be called once', 'called twice'))

    def test_when_expected_to_once_raise_exception_and_called_once__then_pass(self):
        self.foo.expect_call().will_once(Raise(Exception('an error')))
        with pytest.raises(Exception) as excinfo:
            self.foo()
        assert str(excinfo.value) == 'an error'
        self.foo.assert_satisfied()


class TestInvoke(TestActionsBase):

    def setup_method(self):
        super().setup_method()
        self.args = []
        self.kwargs = []

    def func(self, *args, **kwargs):
        self.args.append(args)
        self.kwargs.append(kwargs)
        return 'OK'

    ### Tests

    def test_when_expected_to_once_invoke_function_and_called__then_pass_givin_all_args_to_function_and_returning_its_result(self):
        self.foo.expect_call(1, 2, a=3).will_once(Invoke(self.func))
        assert self.foo(1, 2, a=3) == 'OK'
        assert self.args == [(1, 2)]
        assert self.kwargs == [{'a': 3}]
        self.foo.assert_satisfied()

    def test_when_expected_to_once_invoke_function_and_never_called__then_fail(self):
        self.foo.expect_call().will_once(Invoke(self.func))
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo()', "Invoke(func)", 'to be called once', 'never called'))
