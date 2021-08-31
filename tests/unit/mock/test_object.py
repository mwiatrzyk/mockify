import math

import pytest

from mockify import exc
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


def test_if_magic_method_does_not_have_expectation_set_and_does_not_exist_in_base_class_then_issue_uninterested_call_instead(uut, assert_that):
    with pytest.raises(exc.UninterestedCall) as excinfo:
        math.floor(uut)
    actual_call = excinfo.value.actual_call
    assert actual_call.name == 'uut.__floor__'
    assert_that.call_params_match(actual_call)  # called without params


def test_if_magic_method_does_not_have_expectation_set_and_exists_in_base_class_then_call_existing_implementation(uut):
    uut_hash = hash(uut)
    assert isinstance(uut_hash, int)
    assert uut_hash > 0


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
        assert uut <= 123


def test_expect_unary_pos_to_be_used_and_use_it(uut):
    uut.__pos__.expect_call().will_once(Return(1))
    with satisfied(uut):
        assert +uut == 1


def test_expect_unary_neg_to_be_used_and_use_it(uut):
    uut.__neg__.expect_call().will_once(Return(-1))
    with satisfied(uut):
        assert -uut == -1


def test_expect_abs_to_be_called_on_mock_and_call_it(uut):
    uut.__abs__.expect_call().will_once(Return(123))
    with satisfied(uut):
        assert abs(uut) == 123


def test_expect_invert_to_be_called_on_mock_and_call_it(uut):
    uut.__invert__.expect_call().will_once(Return(123))
    with satisfied(uut):
        assert ~uut == 123


def test_expect_round_to_be_called_without_args_and_call_it_without_args(uut):
    uut.__round__.expect_call().will_once(Return(123))
    with satisfied(uut):
        assert round(uut) == 123


def test_expect_round_to_be_called_with_args_and_call_it_with_args(uut):
    uut.__round__.expect_call(2).will_once(Return(123))
    with satisfied(uut):
        assert round(uut, 2) == 123


def test_expect_floor_to_be_called_on_mock_and_call_it(uut):
    uut.__floor__.expect_call().will_once(Return(123))
    with satisfied(uut):
        assert math.floor(uut) == 123


def test_expect_ceil_to_be_called_on_mock_and_call_it(uut):
    uut.__ceil__.expect_call().will_once(Return(123))
    with satisfied(uut):
        assert math.ceil(uut) == 123


def test_expect_trunc_to_be_called_on_mock_and_call_it(uut):
    uut.__trunc__.expect_call().will_once(Return(123))
    with satisfied(uut):
        assert math.trunc(uut) == 123


def test_expect_add_to_be_called_and_call_it(uut):
    uut.__add__.expect_call(1).will_once(Return(3))
    with satisfied(uut):
        assert uut + 1 == 3


def test_expect_sub_to_be_called_and_call_it(uut):
    uut.__sub__.expect_call(1).will_once(Return(1))
    with satisfied(uut):
        assert uut - 1 == 1


def test_expect_mul_to_be_called_and_call_it(uut):
    uut.__mul__.expect_call(2).will_once(Return(4))
    with satisfied(uut):
        assert uut * 2 == 4


def test_expect_floordiv_to_be_called_and_call_it(uut):
    uut.__floordiv__.expect_call(2).will_once(Return(2))
    with satisfied(uut):
        assert uut // 2 == 2


def test_expect_truediv_to_be_called_and_call_it(uut):
    uut.__truediv__.expect_call(2).will_once(Return(2.5))
    with satisfied(uut):
        assert uut / 2 == 2.5


def test_expect_mod_to_be_called_and_call_it(uut):
    uut.__mod__.expect_call(3).will_once(Return(2))
    with satisfied(uut):
        assert uut % 3 == 2


def test_expect_divmod_to_be_called_and_call_it(uut):
    uut.__divmod__.expect_call(3).will_once(Return((2, 0)))
    with satisfied(uut):
        assert divmod(uut, 3) == (2, 0)


def test_expect_pow_to_be_called_and_call_it(uut):
    uut.__pow__.expect_call(2).will_once(Return(16))
    with satisfied(uut):
        assert uut ** 2 == 16


def test_expect_lshift_to_be_called_and_call_it(uut):
    uut.__lshift__.expect_call(2).will_once(Return(16))
    with satisfied(uut):
        assert uut << 2 == 16


def test_expect_rshift_to_be_called_and_call_it(uut):
    uut.__rshift__.expect_call(2).will_once(Return(16))
    with satisfied(uut):
        assert uut >> 2 == 16


def test_expect_and_to_be_called_and_call_it(uut):
    uut.__and__.expect_call(2).will_once(Return(16))
    with satisfied(uut):
        assert uut & 2 == 16


def test_expect_or_to_be_called_and_call_it(uut):
    uut.__or__.expect_call(2).will_once(Return(16))
    with satisfied(uut):
        assert uut | 2 == 16


def test_expect_xor_to_be_called_and_call_it(uut):
    uut.__xor__.expect_call(2).will_once(Return(16))
    with satisfied(uut):
        assert uut ^ 2 == 16


def test_expect_radd_to_be_called_and_call_it(uut):
    uut.__radd__.expect_call(1).will_once(Return(3))
    with satisfied(uut):
        assert 1 + uut == 3


def test_expect_rsub_to_be_called_and_call_it(uut):
    uut.__rsub__.expect_call(1).will_once(Return(1))
    with satisfied(uut):
        assert 1 - uut == 1


def test_expect_rmul_to_be_called_and_call_it(uut):
    uut.__rmul__.expect_call(2).will_once(Return(4))
    with satisfied(uut):
        assert 2 * uut == 4


def test_expect_rfloordiv_to_be_called_and_call_it(uut):
    uut.__rfloordiv__.expect_call(2).will_once(Return(2))
    with satisfied(uut):
        assert 2 // uut == 2


def test_expect_rtruediv_to_be_called_and_call_it(uut):
    uut.__rtruediv__.expect_call(2).will_once(Return(2.5))
    with satisfied(uut):
        assert 2 / uut == 2.5


def test_expect_rmod_to_be_called_and_call_it(uut):
    uut.__rmod__.expect_call(3).will_once(Return(2))
    with satisfied(uut):
        assert 3 % uut == 2


def test_expect_rdivmod_to_be_called_and_call_it(uut):
    uut.__rdivmod__.expect_call(3).will_once(Return((2, 0)))
    with satisfied(uut):
        assert divmod(3, uut) == (2, 0)


def test_expect_rpow_to_be_called_and_call_it(uut):
    uut.__rpow__.expect_call(2).will_once(Return(16))
    with satisfied(uut):
        assert 2 ** uut == 16


def test_expect_rlshift_to_be_called_and_call_it(uut):
    uut.__rlshift__.expect_call(2).will_once(Return(16))
    with satisfied(uut):
        assert 2 << uut == 16


def test_expect_rrshift_to_be_called_and_call_it(uut):
    uut.__rrshift__.expect_call(2).will_once(Return(16))
    with satisfied(uut):
        assert 2 >> uut == 16


def test_expect_rand_to_be_called_and_call_it(uut):
    uut.__rand__.expect_call(2).will_once(Return(16))
    with satisfied(uut):
        assert 2 & uut == 16


def test_expect_ror_to_be_called_and_call_it(uut):
    uut.__ror__.expect_call(2).will_once(Return(16))
    with satisfied(uut):
        assert 2 | uut == 16


def test_expect_rxor_to_be_called_and_call_it(uut):
    uut.__rxor__.expect_call(2).will_once(Return(16))
    with satisfied(uut):
        assert 2 ^ uut == 16


def test_expect_iadd_to_be_called_and_call_it(uut):
    uut.__iadd__.expect_call(1)
    with satisfied(uut):
        uut += 1


def test_expect_isub_to_be_called_and_call_it(uut):
    uut.__isub__.expect_call(1)
    with satisfied(uut):
        uut -= 1


def test_expect_imul_to_be_called_and_call_it(uut):
    uut.__imul__.expect_call(2)
    with satisfied(uut):
        uut *= 2


def test_expect_ifloordiv_to_be_called_and_call_it(uut):
    uut.__ifloordiv__.expect_call(2)
    with satisfied(uut):
        uut //= 2


def test_expect_itruediv_to_be_called_and_call_it(uut):
    uut.__itruediv__.expect_call(2)
    with satisfied(uut):
        uut /= 2


def test_expect_imod_to_be_called_and_call_it(uut):
    uut.__imod__.expect_call(3)
    with satisfied(uut):
        uut %= 3


def test_expect_ipow_to_be_called_and_call_it(uut):
    uut.__ipow__.expect_call(2)
    with satisfied(uut):
        uut **= 2


def test_expect_ilshift_to_be_called_and_call_it(uut):
    uut.__ilshift__.expect_call(2)
    with satisfied(uut):
        uut <<= 2


def test_expect_irshift_to_be_called_and_call_it(uut):
    uut.__irshift__.expect_call(2)
    with satisfied(uut):
        uut >>= 2


def test_expect_iand_to_be_called_and_call_it(uut):
    uut.__iand__.expect_call(2)
    with satisfied(uut):
        uut &= 2


def test_expect_ior_to_be_called_and_call_it(uut):
    uut.__ior__.expect_call(2)
    with satisfied(uut):
        uut |= 2


def test_expect_ixor_to_be_called_and_call_it(uut):
    uut.__ixor__.expect_call(2)
    with satisfied(uut):
        uut ^= 2


def test_when_expectation_is_recorded_on_div_magic_method_then_it_is_equivalent_to_recording_on_truediv_magic_method(uut):
    uut.__div__.expect_call(2).will_once(Return(2.5))
    with satisfied(uut):
        assert uut / 2 == 2.5


def test_when_expectation_is_recorded_on_rdiv_magic_method_then_it_is_equivalent_to_recording_on_rtruediv_magic_method(uut):
    uut.__rdiv__.expect_call(2).will_once(Return(2.5))
    with satisfied(uut):
        assert 2 / uut == 2.5


def test_when_expectation_is_recorded_on_idiv_magic_method_then_it_is_equivalent_to_recording_on_itruediv_magic_method(uut):
    uut.__idiv__.expect_call(2)
    with satisfied(uut):
        uut /= 2


def test_expect_hash_to_be_called_and_call_it(uut):
    uut.__hash__.expect_call().will_once(Return(123))
    with satisfied(uut):
        assert hash(uut) == 123


def test_expect_sizeof_to_be_called_and_call_it(uut):
    uut.__sizeof__.expect_call().will_once(Return(32))
    with satisfied(uut):
        assert uut.__sizeof__() == 32


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
