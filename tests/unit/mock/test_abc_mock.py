import abc

import pytest

from mockify import satisfied
from mockify.mock import ABCMock
from mockify.actions import Return


class TestABCMock:

    def test_when_creating_mock_with_abstract_base_class_not_being_a_class__type_error_is_raised(self):
        with pytest.raises(TypeError) as excinfo:
            ABCMock('uut', object())
        assert str(excinfo.value) == "__init__() got an invalid value for argument 'abstract_base_class'"

    def test_when_creating_mock_with_abstract_base_class_not_being_a_subclass_of_abc__type_error_is_raised(self):
        with pytest.raises(TypeError) as excinfo:
            ABCMock('uut', object)
        assert str(excinfo.value) == "__init__() got an invalid value for argument 'abstract_base_class'"

    def test_created_mock_object_is_instance_of_given_abstract_base_class(self):

        class IFoo(abc.ABC):
            pass

        uut = ABCMock('uut', IFoo)

        assert isinstance(uut, IFoo)

    def test_if_method_is_not_defined_in_the_interface__it_does_not_exist_in_mock(self):

        class IFoo(abc.ABC):
            @abc.abstractmethod
            def foo(self):
                pass

        uut = ABCMock('uut', IFoo)

        with pytest.raises(AttributeError) as excinfo:
            uut.bar.expect_call()

        assert str(excinfo.value) == "'ABCMock' object has no attribute 'bar'"

    def test_if_property_is_not_defined_in_the_interface__recording_getattr_expectation_fails_with_attribute_error(self):

        class IFoo(abc.ABC):
            @property
            @abc.abstractmethod
            def foo(self):
                pass

        uut = ABCMock('uut', IFoo)

        with pytest.raises(AttributeError) as excinfo:
            uut.__getattr__.expect_call('bar')

        assert str(excinfo.value) == "'ABCMock' object has no attribute 'bar'"

    def test_if_property_is_not_defined_in_the_interface__recording_setattr_expectation_fails_with_attribute_error(self):

        class IFoo(abc.ABC):
            @property
            @abc.abstractmethod
            def foo(self):
                pass

        uut = ABCMock('uut', IFoo)

        with pytest.raises(AttributeError) as excinfo:
            uut.__setattr__.expect_call('bar', 123)

        assert str(excinfo.value) == "can't set attribute 'bar'"

    def test_if_method_call_expectation_is_recorded_with_invalid_number_of_positional_args__then_fail_with_type_error(self):

        class IFoo(abc.ABC):
            @abc.abstractmethod
            def foo(self, a, b):
                pass

        uut = ABCMock('uut', IFoo)

        with pytest.raises(TypeError) as excinfo:
            uut.foo.expect_call(1, 2, 3)

        assert str(excinfo.value) == "uut.foo(a, b): too many positional arguments"

    def test_if_method_call_expectation_is_recorded_with_invalid_argument_names__then_fail_with_type_error(self):

        class IFoo(abc.ABC):
            @abc.abstractmethod
            def foo(self, a, b):
                pass

        uut = ABCMock('uut', IFoo)

        with pytest.raises(TypeError) as excinfo:
            uut.foo.expect_call(a=1, bb=2)

        assert str(excinfo.value) == "uut.foo(a, b): missing a required argument: 'b'"

    def test_record_and_consume_abstract_method_call_expectation(self):

        class IFoo(abc.ABC):
            @abc.abstractmethod
            def foo(self, a, b):
                pass

        uut = ABCMock('uut', IFoo)
        uut.foo.expect_call(1, 2).will_once(Return(3))

        with satisfied(uut):
            assert uut.foo(1, 2) == 3
