import abc

import pytest

from mockify import exc, satisfied, assert_satisfied
from mockify.mock import ABCMock
from mockify.actions import Return


class IDummy(abc.ABC):

    @property
    @abc.abstractmethod
    def foo(self):
        pass

    @abc.abstractmethod
    def spam(self, a, b):
        pass


class TestABCMock:
    _valid_names = ['foo', 'bar', 'foo.bar', 'foo.bar.baz']

    @pytest.fixture(autouse=True)
    def setup(self):
        self.uut = ABCMock('uut', IDummy)

    def test_when_creating_mock_with_abstract_base_class_not_being_a_class__type_error_is_raised(self):
        with pytest.raises(TypeError) as excinfo:
            ABCMock('uut', object())
        assert str(excinfo.value) == "__init__() got an invalid value for argument 'abstract_base_class'"

    def test_when_creating_mock_with_abstract_base_class_not_being_a_subclass_of_abc__type_error_is_raised(self):
        with pytest.raises(TypeError) as excinfo:
            ABCMock('uut', object)
        assert str(excinfo.value) == "__init__() got an invalid value for argument 'abstract_base_class'"

    def test_created_mock_object_is_instance_of_given_abstract_base_class(self):
        assert isinstance(self.uut, IDummy)

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

        assert str(excinfo.value) == "can't set attribute 'bar' (not defined in the interface)"

    def test_when_no_getattr_expectation_set_on_property__getting_it_raises_uninterested_call(self):
        with pytest.raises(exc.UninterestedCall) as excinfo:
            foo = self.uut.foo
        assert str(excinfo.value.actual_call) == "uut.__getattr__('foo')"

    def test_when_no_setattr_expectation_set_on_property__setting_it_raises_uninterested_call(self):
        with pytest.raises(exc.UninterestedCall) as excinfo:
            self.uut.foo = 123
        assert str(excinfo.value.actual_call) == "uut.__setattr__('foo', 123)"

    def test_cannot_set_property_that_is_not_declared_in_the_interface(self):
        with pytest.raises(AttributeError) as excinfo:
            self.uut.bar = 123
        assert str(excinfo.value) == "can't set attribute 'bar' (not defined in the interface)"

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

    @pytest.mark.parametrize('name', _valid_names)
    def test_get_mock_name(self, name):
        assert ABCMock(name, IDummy).__m_name__ == name

    @pytest.mark.parametrize('name', _valid_names)
    def test_get_mock_fullname(self, name):
        assert ABCMock(name, IDummy).__m_fullname__ == name

    def test_get_fullname_of_a_method(self):
        assert self.uut.spam.__m_fullname__ == 'uut.spam'

    def test_list_mock_children(self):
        children = set(self.uut.__m_children__())
        assert len(children) == 3  # __getattr__, __setattr__ and spam
        assert children == set([self.uut.__getattr__, self.uut.__setattr__, self.uut.spam])

    def test_method_mock_has_empty_list_of_children(self):
        assert set(self.uut.spam.__m_children__()) == set()

    def test_mock_has_empty_set_of_expectations(self):
        self.uut.spam.expect_call(1, 2)
        assert set(self.uut.__m_expectations__()) == set()

    def test_list_expectations_of_a_method(self):
        one = self.uut.spam.expect_call(1, 2)
        two = self.uut.spam.expect_call(3, 4)
        three = self.uut.__getattr__.expect_call('foo')
        assert set(self.uut.spam.__m_expectations__()) == set([one, two])

    def test_expect_getattr_and_consume_expectation(self):
        self.uut.__getattr__.expect_call('foo').will_once(Return(123))
        with satisfied(self.uut):
            assert self.uut.foo == 123

    def test_expect_setattr_and_consume_expectation(self):
        self.uut.__setattr__.expect_call('foo', 123)
        with satisfied(self.uut):
            self.uut.foo = 123

    def test_expect_method_call_and_consume_expectation(self):
        self.uut.spam.expect_call(1, 2).will_once(Return(123))
        with satisfied(self.uut):
            assert self.uut.spam(1, 2) == 123

    def test_if_method_is_called_with_invalid_arguments__then_type_error_is_raised(self):
        with pytest.raises(TypeError) as excinfo:
            self.uut.spam(1, 2, 3)
        assert str(excinfo.value) == "uut.spam(a, b): too many positional arguments"

    def test_when_expectations_are_not_satisfied__unsatisfied_error_is_raised(self):
        one = self.uut.__getattr__.expect_call('foo')
        two = self.uut.__setattr__.expect_call('foo', 123)
        three = self.uut.spam.expect_call(1, 2)
        with pytest.raises(exc.Unsatisfied) as excinfo:
            assert_satisfied(self.uut)
        assert excinfo.value.unsatisfied_expectations == [one, two, three]
