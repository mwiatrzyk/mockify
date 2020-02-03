import pytest

from mockify import exc, satisfied
from mockify.mock import Mock
from mockify.actions import Return


@pytest.fixture
def uut():
    return Mock('uut')


class TestMock:

    def test_expect_mock_to_be_called_as_a_function_and_call_it(self, uut):
        uut.expect_call(1, 2)
        with satisfied(uut):
            uut(1, 2)

    def test_expect_mock_property_to_be_called_as_a_method_and_call_it(self, uut):
        uut.foo.expect_call(1)
        with satisfied(uut):
            uut.foo(1)

    def test_expect_two_mock_properties_to_be_called_as_a_method_and_call_them(self, uut):
        uut.foo.expect_call(1)
        uut.bar.expect_call(2)
        with satisfied(uut):
            uut.foo(1)
            uut.bar(2)

    def test_expect_namespaced_property_to_be_called_as_a_method_and_call_it(self, uut):
        uut.foo.bar.expect_call(1)
        with satisfied(uut):
            uut.foo.bar(1)

    def test_expect_double_namespaced_property_to_be_called_as_a_method_and_call_it(self, uut):
        uut.foo.bar.baz.expect_call(1)
        with satisfied(uut):
            uut.foo.bar.baz(1)

    def test_expect_expect_call_to_be_called_and_call_it(self, uut):
        uut.expect_call.expect_call(1)
        with satisfied(uut):
            uut.expect_call(1)

    def test_expect_namespaced_expect_call_to_be_called_and_call_it(self, uut):
        uut.foo.expect_call.expect_call(1)
        with satisfied(uut):
            uut.foo.expect_call(1)

    def test_expect_property_get_and_get_it(self, uut):
        uut.__getattr__.expect_call('foo').will_once(Return(1))
        with satisfied(uut):
            assert uut.foo == 1

    def test_when_property_already_exists__it_is_not_possible_to_record_get_expectation(self, uut):
        _ = uut.foo
        with pytest.raises(TypeError) as excinfo:
            uut.__getattr__.expect_call('foo').will_once(Return(1))
        assert str(excinfo.value) ==\
            "__getattr__.expect_call() must be called with a non existing "\
            "property name, got 'foo' which already exists"

    def test_expect_namespaced_property_get_and_get_it(self, uut):
        uut.foo.__getattr__.expect_call('bar').will_once(Return(1))
        with satisfied(uut):
            assert uut.foo.bar == 1

    def test_when_namespaced_property_already_exists__it_is_not_possible_to_record_get_expectation(self, uut):
        _ = uut.foo.bar
        with pytest.raises(TypeError) as excinfo:
            uut.foo.__getattr__.expect_call('bar').will_once(Return(1))
        assert str(excinfo.value) ==\
            "__getattr__.expect_call() must be called with a non existing "\
            "property name, got 'bar' which already exists"

    def test_when_property_get_expectation_is_recorded_with_invalid_number_of_params__then_raise_type_error(self, uut):
        with pytest.raises(TypeError) as excinfo:
            uut.__getattr__.expect_call('foo', 'bar')
        assert str(excinfo.value) == "expect_call() takes 2 positional arguments but 3 were given"

    @pytest.mark.parametrize('invalid_name', [
        '123',
        [],
        '@#$',
        '123foo'
    ])
    def test_when_property_get_expectation_is_recorded_with_invalid_property_name__then_raise_type_error(self, uut, invalid_name):
        with pytest.raises(TypeError) as excinfo:
            uut.__getattr__.expect_call(invalid_name)
        assert str(excinfo.value) ==\
            f"__getattr__.expect_call() must be called with valid Python property name, got {invalid_name!r}"

    def test_when_property_is_expected_to_be_get_and_is_never_get__then_raise_unsatisfied_error(self, uut):
        expectation = uut.__getattr__.expect_call('spam')
        with pytest.raises(exc.Unsatisfied) as excinfo:
            with satisfied(uut):
                pass
        unsatisfied_expectations = excinfo.value.unsatisfied_expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] == expectation

    def test_when_property_is_set__getting_it_returns_same_value(self, uut):
        uut.foo = 123
        assert uut.foo == 123

    def test_when_namespaced_property_is_set__getting_it_returns_same_value(self, uut):
        uut.foo.bar = 123
        assert uut.foo.bar == 123

    def test_expect_property_to_be_set_and_set_it(self, uut):
        uut.__setattr__.expect_call('foo', 123)
        with satisfied(uut):
            uut.foo = 123

    def test_when_property_already_exists__it_is_not_possible_to_record_set_expectation(self, uut):
        uut.foo = 1
        with pytest.raises(TypeError) as excinfo:
            uut.__setattr__.expect_call('foo', 2)
        assert str(excinfo.value) ==\
            "__setattr__.expect_call() must be called with a non existing "\
            "property name, got 'foo' which already exists"

    def test_when_property_set_expectation_is_recorded_with_invalid_number_of_params__then_raise_type_error(self, uut):
        with pytest.raises(TypeError) as excinfo:
            uut.__setattr__.expect_call('foo', 'bar', 'baz')
        assert str(excinfo.value) == "expect_call() takes 3 positional arguments but 4 were given"

    @pytest.mark.parametrize('invalid_name', [
        '123',
        [],
        '@#$',
        '123foo'
    ])
    def test_when_property_set_expectation_is_recorded_with_invalid_property_name__then_raise_type_error(self, uut, invalid_name):
        with pytest.raises(TypeError) as excinfo:
            uut.__setattr__.expect_call(invalid_name, 123)
        assert str(excinfo.value) ==\
            f"__setattr__.expect_call() must be called with valid Python property name, got {invalid_name!r}"

    def test_when_property_is_expected_to_be_set_and_is_never_set__then_raise_unsatisfied_error(self, uut):
        expectation = uut.__setattr__.expect_call('spam', 123)
        with pytest.raises(exc.Unsatisfied) as excinfo:
            with satisfied(uut):
                pass
        unsatisfied_expectations = excinfo.value.unsatisfied_expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] == expectation

    def test_record_set_and_get_expectations_for_same_property(self, uut):
        uut.__setattr__.expect_call('foo', 123)
        uut.__getattr__.expect_call('foo').will_once(Return(123))
        with satisfied(uut):
            uut.foo = 123
            assert uut.foo == 123

    def test_when_action_chain_is_recorded__invoking_mock_consumes_actions_one_by_one(self, uut):
        uut.expect_call().\
            will_once(Return(1)).\
            will_once(Return(2)).\
            will_once(Return(3))
        with satisfied(uut):
            assert [uut() for _ in range(3)] == [1, 2, 3]
