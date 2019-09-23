import pytest

from mockify.actions import Return

from _mockify import Call
from _mockify.mock import Mock
from _mockify.actions import Iterate  # TODO: import from mockify once this is available
from _mockify.matchers import InstanceOf, Any  # TODO: use InstanceOf from mockify

_CALL_PARAMS = [
    (tuple(), {}),
    ((1,), {'a': 2}),
    ((1, 2), {'c': 3, 'd': 4}),
]


class TestMock:

    @pytest.fixture(autouse=True)
    def make_uut(self, registry_stub, mock_factory):
        self.registry_stub = registry_stub
        self.uut = Mock('uut', registry=self.registry_stub)

    def test_mock_repr(self):
        assert repr(self.uut) == "<mockify.mock.Mock('uut')>"

    @pytest.mark.parametrize('params', _CALL_PARAMS)
    def test_call(self, params):
        args, kwargs = params
        self.uut(*args, **kwargs)
        assert self.registry_stub.calls == [Call('uut', *args, **kwargs)]

    @pytest.mark.parametrize('params', _CALL_PARAMS)
    def test_call_method(self, params):
        args, kwargs = params
        self.uut.foo(*args, **kwargs)
        assert self.registry_stub.calls == [Call('uut.foo', *args, **kwargs)]

    @pytest.mark.parametrize('params', _CALL_PARAMS)
    def test_call_namespaced_method(self, params):
        args, kwargs = params
        self.uut.foo.bar(*args, **kwargs)
        assert self.registry_stub.calls == [Call('uut.foo.bar', *args, **kwargs)]

    @pytest.mark.parametrize('params', _CALL_PARAMS)
    def test_record_call_expectation(self, params):
        args, kwargs = params
        self.uut.expect_call(*args, **kwargs)
        assert self.registry_stub.expected_calls == [Call('uut', *args, **kwargs)]

    @pytest.mark.parametrize('params', _CALL_PARAMS)
    def test_record_method_call_expectation(self, params):
        args, kwargs = params
        self.uut.foo.expect_call(*args, **kwargs)
        assert self.registry_stub.expected_calls == [Call('uut.foo', *args, **kwargs)]

    @pytest.mark.parametrize('params', _CALL_PARAMS)
    def test_record_namespaced_method_call_expectation(self, params):
        args, kwargs = params
        self.uut.foo.bar.expect_call(*args, **kwargs)
        assert self.registry_stub.expected_calls == [Call('uut.foo.bar', *args, **kwargs)]

    def test_when_property_is_set__then_getting_it_returns_its_value(self):
        self.uut.foo = 123
        assert self.uut.foo == 123

    def test_getting_property_returns_mock_attr_instance(self):
        assert isinstance(self.uut.foo, Mock.Attr)

    def test_getting_property_twice_returns_same_object(self):
        assert id(self.uut.foo) == id(self.uut.foo)

    def test_when_property_get_expectation_is_recorded__getting_a_property_triggers_registry(self):
        self.uut.__getattr__.expect_call('foo')
        assert self.registry_stub.expected_calls == [Call('uut.__getattr__', 'foo')]
        foo = self.uut.foo
        assert self.registry_stub.calls == [Call('uut.__getattr__', 'foo')]

    def test_when_property_get_expectation_is_recorded__getting_another_property_returns_mock_attr_instance(self):
        self.uut.__getattr__.expect_call('foo')
        assert self.registry_stub.expected_calls == [Call('uut.__getattr__', 'foo')]
        assert isinstance(self.uut.bar, Mock.Attr)
        assert self.registry_stub.calls == []

    def test_when_property_get_expect_call_is_triggered_with_no_arguments__then_type_error_is_raised(self):
        with pytest.raises(TypeError) as excinfo:
            self.uut.__getattr__.expect_call()
        assert str(excinfo.value) == "uut.__getattr__.expect_call() missing 1 required positional argument: 'name'"

    def test_when_property_get_expect_call_is_triggered_with_two_arguments__then_type_error_is_raised(self):
        with pytest.raises(TypeError) as excinfo:
            self.uut.__getattr__.expect_call('foo', 123)
        assert str(excinfo.value) == "uut.__getattr__.expect_call() takes 2 positional arguments but 3 were given"

    def test_when_property_set_expectation_is_recorded__then_setting_property_triggers_registry(self):
        self.uut.__setattr__.expect_call('foo', 123)
        assert self.registry_stub.expected_calls == [Call('uut.__setattr__', 'foo', 123)]
        self.uut.foo = 123
        assert self.registry_stub.calls == [Call('uut.__setattr__', 'foo', 123)]

    def test_when_property_set_expectation_is_recorded__then_setting_property_to_another_value_triggers_registry(self):
        self.uut.__setattr__.expect_call('foo', 123)
        assert self.registry_stub.expected_calls == [Call('uut.__setattr__', 'foo', 123)]
        self.uut.foo = 124
        assert self.registry_stub.calls == [Call('uut.__setattr__', 'foo', 124)]

    def test_when_property_set_expectation_is_recorded__then_setting_another_property_just_sets_a_value(self):
        self.uut.__setattr__.expect_call('foo', 123)
        assert self.registry_stub.expected_calls == [Call('uut.__setattr__', 'foo', 123)]
        self.uut.foo = 123
        assert self.registry_stub.calls == [Call('uut.__setattr__', 'foo', 123)]
        self.uut.bar = 456
        assert self.uut.bar == 456

    def test_when_property_set_expect_call_is_called_without_arguments__then_raise_type_error(self):
        with pytest.raises(TypeError) as excinfo:
            self.uut.__setattr__.expect_call()
        assert str(excinfo.value) == "uut.__setattr__.expect_call() missing 2 required positional arguments: 'name' and 'value'"

    def test_when_property_set_expect_call_is_called_with_one_argument__then_raise_type_error(self):
        with pytest.raises(TypeError) as excinfo:
            self.uut.__setattr__.expect_call('foo')
        assert str(excinfo.value) == "uut.__setattr__.expect_call() missing 1 required positional argument: 'value'"

    def test_when_property_set_expect_call_is_called_with_three_arguments__then_raise_type_error(self):
        with pytest.raises(TypeError) as excinfo:
            self.uut.__setattr__.expect_call('foo', 1, 2)
        assert str(excinfo.value) == "uut.__setattr__.expect_call() takes 3 positional arguments but 4 were given"

    def test_set_and_get_namespaced_property(self):
        self.uut.foo.bar = 123
        assert self.uut.foo.bar == 123

    def test_when_namespaced_property_get_expectation_is_recorded__getting_a_property_triggers_registry(self):
        self.uut.foo.__getattr__.expect_call('bar')
        assert self.registry_stub.expected_calls == [Call('uut.foo.__getattr__', 'bar')]
        bar = self.uut.foo.bar
        assert self.registry_stub.calls == [Call('uut.foo.__getattr__', 'bar')]

    def test_when_namespaced_property_set_expectation_is_recorded__then_setting_property_triggers_registry(self):
        self.uut.foo.__setattr__.expect_call('bar', 123)
        assert self.registry_stub.expected_calls == [Call('uut.foo.__setattr__', 'bar', 123)]
        self.uut.foo.bar = 123
        assert self.registry_stub.calls == [Call('uut.foo.__setattr__', 'bar', 123)]

    def test_call_assert_satisfied_when_no_expectations_are_recorded(self):
        self.uut.assert_satisfied()
        self.registry_stub.checked_mock_names == []

    def test_when_assert_satisfied_is_called_on_nested_property__then_call_registry(self):
        self.uut.foo.assert_satisfied()
        assert self.registry_stub.calls == [Call('uut.foo.assert_satisfied')]

    def test_when_expect_call_method_is_expected_to_be_called__then_calling_it_calls_registry(self):
        self.uut.expect_call.expect_call(1, 2, c=3)
        assert self.registry_stub.expected_calls == [Call('uut.expect_call', 1, 2, c=3)]
        self.uut.expect_call(1, 2, c=3)
        assert self.registry_stub.calls == [Call('uut.expect_call', 1, 2, c=3)]

    def test_when_assert_satisfied_method_is_expected_to_be_called__then_calling_it_calls_registry(self):
        self.uut.assert_satisfied.expect_call()
        assert self.registry_stub.expected_calls == [Call('uut.assert_satisfied')]
        self.uut.assert_satisfied()
        assert self.registry_stub.calls == [Call('uut.assert_satisfied')]

    def test_when_assert_satisfied_is_called_after_expectations_are_recorded__then_it_collects_all_expected_mock_names(self):
        self.uut.foo.expect_call(1)
        self.uut.bar.baz.expect_call(2)
        self.uut.expect_call(3)
        self.uut.spam.__getattr__.expect_call('more_spam')
        self.uut.assert_satisfied()
        assert self.registry_stub.checked_mock_names == [
            'uut.foo', 'uut.bar.baz', 'uut', 'uut.spam.__getattr__']
