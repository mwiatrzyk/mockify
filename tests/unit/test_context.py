import pytest

from mockify import exc
from mockify.cardinality import Exactly

from mockify.core.mock import MockCall
from mockify.core.context import Context


class MockStub:

    def __init__(self, ctx, name):
        self.ctx = ctx
        self.name = name


class ExpectationStub:

    def __init__(self, mock_call, filename, lineno):
        self.mock_call = mock_call
        self.filename = filename
        self.lineno = lineno
        self.call_count = Exactly(1)

    def __call__(self, *args, **kwargs):
        self.call_count.update()

    def __eq__(self, other):
        return self.mock_call == other.mock_call and\
            self.filename == other.filename and\
            self.lineno == other.lineno

    def is_satisfied(self):
        return self.call_count.is_satisfied()


class TestContext:

    def setup_method(self):
        self.ctx = Context(mock_class=MockStub, expectation_class=ExpectationStub)

    ### Tests

    def test_when_creating_a_mock__then_instance_of_given_mock_class_is_created(self):
        mock = self.ctx.make_mock("mock")
        assert isinstance(mock, MockStub)
        assert mock.ctx is self.ctx
        assert mock.name == "mock"

    def test_when_creating_multiple_mocks_at_once__then_multiple_instances_of_given_mock_class_are_created(self):
        foo, bar = self.ctx.make_mocks("foo", "bar")
        assert isinstance(foo, MockStub)
        assert isinstance(bar, MockStub)
        assert foo.name == "foo"
        assert bar.name == "bar"

    def test_with_one_unsatisfied_expectation_registered_and_none_resolved__context_is_not_satisfied(self):
        self.ctx.expect_call("foo", (1, 2), {}, "dummy.py", 1)
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        assert excinfo.value.expectations == [
            ExpectationStub(MockCall("foo", (1, 2), {}), "dummy.py", 1)
        ]

    def test_with_two_unsatisfied_expectations_registered_and_none_resolved__context_is_not_satisfied(self):
        self.ctx.expect_call("foo", (1, 2), {}, "dummy.py", 1)
        self.ctx.expect_call("bar", (1, 2), {}, "dummy.py", 2)
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        assert excinfo.value.expectations == [
            ExpectationStub(MockCall("foo", (1, 2), {}), "dummy.py", 1),
            ExpectationStub(MockCall("bar", (1, 2), {}), "dummy.py", 2)
        ]

    def test_with_two_unsatisfied_expectations_registered_and_one_resolved__context_is_not_satisfied(self):
        self.ctx.expect_call("foo", (1, 2), {}, "dummy.py", 1)
        self.ctx.expect_call("bar", (1, 2), {}, "dummy.py", 2)
        self.ctx("foo", (1, 2), {})
        with pytest.raises(exc.Unsatisfied) as excinfo:
            self.ctx.assert_satisfied()
        assert excinfo.value.expectations == [
            ExpectationStub(MockCall("bar", (1, 2), {}), "dummy.py", 2)
        ]

    def test_with_one_expectation_registered_and_one_resolved__context_is_satisfied(self):
        self.ctx.expect_call("foo", (1, 2), {}, "dummy.py", 1)
        self.ctx("foo", (1, 2), {})
        self.ctx.assert_satisfied()

    def test_use_with_statement_with_context_object_to_ensure_that_wrapped_statement_satisfies_all_mocks(self):
        self.ctx.expect_call("foo", tuple(), {}, "dummy.py", 1)
        with pytest.raises(exc.Unsatisfied):
            with self.ctx:
                pass
        with self.ctx:
            self.ctx("foo", tuple(), {})
