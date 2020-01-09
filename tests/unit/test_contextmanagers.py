import pytest

from mockify import ordered, satisfied
from mockify.mock import Mock, MockFactory, MockInfo


class TestOrdered:

    def test_when_called_with_mocks_that_does_not_share_one_session__then_raise_type_error(self):
        first = Mock('first')
        second = Mock('second')
        with pytest.raises(TypeError) as excinfo:
            with ordered(first, second):
                first()
                second()
        assert str(excinfo.value) == "Mocks 'first' and 'second' have to use same session object"

    def test_run_ordered_expectations_for_two_distinct_mocks(self):
        factory = MockFactory()
        first, second = factory.first, factory.second
        first.expect_call(1, 2)
        second.expect_call()
        with satisfied(factory):
            with ordered(first, second):
                first(1, 2)
                second()
