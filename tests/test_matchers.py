import pytest

from mockify import exc
from mockify.mock import FunctionMock
from mockify.matchers import _

from tests.mixins import AssertUnsatisfiedAssertionMatchMixin


class TestMatchersBase(AssertUnsatisfiedAssertionMatchMixin):

    def setup_method(self):
        self.foo = FunctionMock('foo')


class TestAny(TestMatchersBase):

    def test_when_expected_to_be_called_once_with_any_arg_and_never_called__then_fail(self):
        self.foo.expect_call(_)
        with pytest.raises(exc.UnsatisfiedAssertion) as excinfo:
            self.foo.assert_satisfied()
        self.assert_unsatisfied_assertion_match(excinfo,
            ('foo(_)', None, 'to be called once', 'never called'))

    def test_when_expected_to_be_called_once_with_any_arg_and_called_once__then_pass(self):
        self.foo.expect_call(_)
        self.foo('foo')
        self.foo.assert_satisfied()

    def test_when_expected_to_be_called_twice_with_any_arg_and_called_twice__then_pass(self):
        self.foo.expect_call(_).times(2)
        self.foo(1)
        self.foo('foo')
        self.foo.assert_satisfied()
