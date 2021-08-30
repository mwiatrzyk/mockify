import sys

import pytest

from mockify.core import satisfied
from mockify.mock import ObjectMock, FunctionMock
from mockify.actions import Return, Iterate


@pytest.fixture
def uut():
    return ObjectMock('uut')


def test_register_method_call_expectation_and_call_that_method(uut):
    uut.spam.expect_call(1, 2, 3).will_once(Return(123))
    with satisfied(uut):
        uut.spam(1, 2, 3)


def test_expect_object_to_be_called_like_a_function_and_call_it(uut):
    uut.expect_call(1, 2, 3).will_once(Return(123))
    with satisfied(uut):
        assert uut(1, 2, 3) == 123


def test_expect_equals_to_operator_to_be_used_and_use_it(uut):
    uut.__eq__.expect_call(123).will_once(Return(True))
    with satisfied(uut):
        assert uut == 123


def test_expect_not_equals_to_operator_to_be_used_and_use_it(uut):
    uut.__ne__.expect_call(123).will_once(Return(True))
    with satisfied(uut):
        assert uut != 123


def test_expect_less_than_operator_to_be_used_and_use_it(uut):
    uut.__lt__.expect_call(123).will_once(Return(True))
    with satisfied(uut):
        assert uut < 123


def test_expect_greater_than_operator_to_be_used_and_use_it(uut):
    uut.__gt__.expect_call(123).will_once(Return(True))
    with satisfied(uut):
        assert uut > 123


def test_expect_greater_or_equal_operator_to_be_used_and_use_it(uut):
    uut.__ge__.expect_call(123).will_once(Return(True))
    with satisfied(uut):
        assert uut >= 123


def test_expect_less_or_equal_operator_to_be_used_and_use_it(uut):
    uut.__le__.expect_call(123).will_once(Return(True))
    with satisfied(uut):
        assert uut <= 1234


def test_expect_hash_to_be_called_and_call_it(uut):
    uut.__hash__.expect_call().will_once(Return(123))
    with satisfied(uut):
        assert hash(uut) == 123


def test_expect_sizeof_to_be_called_and_call_it(uut):
    uut.__sizeof__.expect_call().will_once(Return(0))
    with satisfied(uut):
        assert sys.getsizeof(uut) == 24  # GC padding; can't find docs, just StackOverflow...


def test_expect_str_call_and_then_call_str_on_mock(uut):
    uut.__str__.expect_call().will_once(Return('dummy'))
    with satisfied(uut):
        assert str(uut) == 'dummy'


def test_if_str_is_called_without_expectation_set_then_return_mocks_repr(uut):
    assert str(uut) == "<mockify.mock._object.ObjectMock('uut')>"


def test_expect_repr_call_and_call_it(uut):
    uut.__repr__.expect_call().will_once(Return('uut'))
    with satisfied(uut):
        assert repr(uut) == 'uut'


def test_if_repr_is_called_without_expectation_set_then_return_default_mock_repr(uut):
    assert repr(uut) == "<mockify.mock._object.ObjectMock('uut')>"


def test_expect_getattr_to_be_called_and_call_it(uut):
    uut.__getattr__.expect_call('foo').will_once(Return(123))
    with satisfied(uut):
        assert uut.foo == 123


def test_expect_setattr_to_be_called_and_call_it(uut):
    uut.__setattr__.expect_call('foo', 123).times(1)
    with satisfied(uut):
        uut.foo = 123


def test_expect_delattr_to_be_called_and_call_it(uut):
    uut.__delattr__.expect_call('foo').times(1)
    with satisfied(uut):
        del uut.foo


def test_expect_getitem_to_be_called_and_call_it(uut):
    uut.__getitem__.expect_call('foo').will_once(Return(123))
    with satisfied(uut):
        assert uut['foo'] == 123


def test_expect_setitem_to_be_called_and_call_it(uut):
    uut.__setitem__.expect_call('foo', 123).times(1)
    with satisfied(uut):
        uut['foo'] = 123


def test_expect_delitem_to_be_called_and_call_it(uut):
    uut.__delitem__.expect_call('foo').times(1)
    with satisfied(uut):
        del uut['foo']


def test_object_mock_allows_to_set_and_get_properties(uut):
    uut.foo = 123
    assert uut.foo == 123
    del uut.foo


def test_object_mock_allows_to_set_and_get_items(uut):
    uut['foo'] = 123
    assert uut['foo'] == 123
    del uut['foo']


def test_object_mock_allows_to_set_and_get_both_items_and_attrs_allowing_name_reuse_for_different_purposes(uut):
    uut.foo = 123
    uut['foo'] = 'spam'
    assert uut.foo == 123
    assert uut['foo'] == 'spam'


def test_expect_iter_to_be_called_and_call_it(uut):
    uut.__iter__.expect_call().will_once(Iterate([1, 2, 3]))
    with satisfied(uut):
        assert list(uut) == [1, 2, 3]


def test_expect_contains_to_be_called_and_call_it(uut):
    uut.__contains__.expect_call('foo').will_once(Return(True))
    uut.__contains__.expect_call('bar').will_once(Return(False))
    with satisfied(uut):
        assert 'foo' in uut
        assert 'bar' not in uut


def test_expect_context_enter_and_enter_context(uut):
    uut.__enter__.expect_call().will_once(Return(123))
    with satisfied(uut):
        with uut as foo:
            assert foo == 123


@pytest.mark.asyncio
async def test_expect_async_context_enter_and_enter_async_context(uut):
    uut.__aenter__.expect_call().will_once(Return(123))
    with satisfied(uut):
        async with uut as foo:
            assert foo == 123
