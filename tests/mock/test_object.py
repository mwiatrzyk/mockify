import pytest

from mockify import exc
from mockify.mock.object import Object
from mockify.mock.function import Function


class TestObject:

    def setup_method(self):
        self.uut = Object('uut', 
                methods=['foo', 'bar'],
                properties=['spam'])

    ### Tests

    def test_when_accessing_attribute_that_is_neither_method_nor_property__then_attribute_error_is_raised(self):
        with pytest.raises(AttributeError) as excinfo:
            ret = self.uut.baz()

        assert str(excinfo.value) == "mock object 'uut' has no attribute named 'baz'"

    def test_when_invoking_a_method_with_unexpected_args__then_uninterested_call_exception_is_raised(self):
        with pytest.raises(exc.UninterestedCall) as excinfo:
            ret = self.uut.foo()

        assert excinfo.value.call.name == self.uut.foo.name

    def test_record_one_expectation_then_invoke_it_and_assert_that_object_is_satisfied(self):
        self.uut.__methods__['foo'].expect_call(1, 2)
        self.uut.foo(1, 2)
        self.uut.assert_satisfied()

    def test_when_two_method_call_expectations_recorded_and_only_one_satisfied__then_object_is_not_satisfied(self):
        self.uut.__methods__['foo'].expect_call(1, 2)
        self.uut.__methods__['bar'].expect_call()
        self.uut.foo(1, 2)
        with pytest.raises(exc.Unsatisfied):
            self.uut.assert_satisfied()

    def test_when_two_method_call_expectations_recorded_and_both_call__then_object_mock_is_satisfied(self):
        self.uut.__methods__['foo'].expect_call()
        self.uut.__methods__['bar'].expect_call()
        self.uut.foo()
        self.uut.bar()
        self.uut.assert_satisfied()

    def test_when_property_set_while_no_expectations_are_recorded__then_fail_with_uninterested_call(self):
        with pytest.raises(exc.UninterestedCall):
            self.uut.spam = 1

    def test_when_setting_property_not_listed_in_properties_list__then_fail_with_attribute_error(self):
        with pytest.raises(AttributeError) as excinfo:
            self.uut.more_spam = 123

        assert str(excinfo.value) == "mock object 'uut' has no property 'more_spam'"

    def test_expect_property_to_be_set_once_and_set_it_once(self):
        self.uut.expect_set('spam', 1)
        self.uut.spam = 1
        self.uut.assert_satisfied()
