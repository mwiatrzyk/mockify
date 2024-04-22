# ---------------------------------------------------------------------------
# tests/unit/mock/test_mock.py
#
# Copyright (C) 2019 - 2024 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import math

import pytest

from mockify import exc
from mockify.api import Iterate, Mock, Raise, Return, _, satisfied
from mockify.matchers import Type


class TestMock:

    @pytest.fixture
    def uut(self):
        return Mock("uut")

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
        uut.__getattr__.expect_call("foo").will_once(Return(1))
        with satisfied(uut):
            assert uut.foo == 1

    def test_expect_namespaced_property_get_and_get_it(self, uut):
        uut.foo.__getattr__.expect_call("bar").will_once(Return(1))
        with satisfied(uut):
            assert uut.foo.bar == 1

    def test_when_property_get_expectation_is_recorded_with_invalid_number_of_params__then_raise_type_error(self, uut):
        with pytest.raises(TypeError) as excinfo:
            uut.__getattr__.expect_call("foo", "bar")
        assert str(excinfo.value).endswith("expect_call() takes 2 positional arguments but 3 were given")

    def test_when_property_is_expected_to_be_get_and_is_never_get__then_raise_unsatisfied_error(self, uut):
        expectation = uut.__getattr__.expect_call("spam")
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
        uut.__setattr__.expect_call("foo", 123)
        with satisfied(uut):
            uut.foo = 123

    def test_when_property_set_expectation_is_recorded_with_invalid_number_of_params__then_raise_type_error(self, uut):
        with pytest.raises(TypeError) as excinfo:
            uut.__setattr__.expect_call("foo", "bar", "baz")
        assert str(excinfo.value).endswith("expect_call() takes 3 positional arguments but 4 were given")

    def test_when_property_is_expected_to_be_set_and_is_never_set__then_raise_unsatisfied_error(self, uut):
        expectation = uut.__setattr__.expect_call("spam", 123)
        with pytest.raises(exc.Unsatisfied) as excinfo:
            with satisfied(uut):
                pass
        unsatisfied_expectations = excinfo.value.unsatisfied_expectations
        assert len(unsatisfied_expectations) == 1
        assert unsatisfied_expectations[0] == expectation

    def test_record_set_and_get_expectations_for_same_property(self, uut):
        uut.__setattr__.expect_call("foo", 123)
        uut.__getattr__.expect_call("foo").will_once(Return(123))
        with satisfied(uut):
            uut.foo = 123
            assert uut.foo == 123

    def test_when_action_chain_is_recorded__invoking_mock_consumes_actions_one_by_one(self, uut):
        uut.expect_call().will_once(Return(1)).will_once(Return(2)).will_once(Return(3))
        with satisfied(uut):
            assert [uut() for _ in range(3)] == [1, 2, 3]

    def test_listing_mock_children_does_only_include_direct_children(self, uut):
        uut.foo.expect_call()
        uut.bar.expect_call()
        uut.spam.more_spam.expect_call()
        assert set(x for x in uut.__m_children__()) == set([uut.foo, uut.bar, uut.spam])

    def test_listing_mock_expectations_does_not_include_child_mock_expectations(self, uut):
        first = uut.expect_call()
        second = uut.expect_call()
        third = uut.foo.expect_call()
        assert set(uut.__m_expectations__()) == set([first, second])
        assert set(uut.foo.__m_expectations__()) == set([third])

    def test_expect_mock_to_be_called_and_call_it(self, uut):
        uut.expect_call(1, 2).will_once(Return(3))
        with satisfied(uut):
            assert uut(1, 2) == 3

    def test_expect_method_to_be_called_and_call_it(self, uut):
        uut.foo.expect_call(1, 2).will_once(Return(3))
        with satisfied(uut):
            assert uut.foo(1, 2) == 3

    def test_expect_namespaced_method_to_be_called_and_call_it(self, uut):
        uut.foo.bar.expect_call(1, 2).will_once(Return(3))
        with satisfied(uut):
            assert uut.foo.bar(1, 2) == 3

    def test_expect_double_namespaced_method_to_be_called_and_call_it(self, uut):
        uut.foo.bar.baz.expect_call(1, 2).will_once(Return(3))
        with satisfied(uut):
            assert uut.foo.bar.baz(1, 2) == 3


class TestMockWithMaxDepthSetToZero:

    @pytest.fixture
    def uut(self):
        return Mock("uut", max_depth=0)

    def test_expect_mock_to_be_called_and_call_it(self, uut):
        uut.expect_call(1, 2).will_once(Return(3))
        with satisfied(uut):
            assert uut(1, 2) == 3

    def test_when_depth_is_zero_then_mocking_methods_is_not_possible(self, uut):
        with pytest.raises(AttributeError) as excinfo:
            uut.foo.expect_call()
        assert str(excinfo.value) == "'FunctionMock' object has no attribute 'foo'"


class TestMockWithMaxDepthSetToOne:

    @pytest.fixture
    def uut(self):
        return Mock("uut", max_depth=1)

    def test_register_method_call_expectation_and_call_that_method(self, uut):
        uut.spam.expect_call(1, 2, 3).will_once(Return(123))
        with satisfied(uut):
            uut.spam(1, 2, 3)

    def test_expect_object_to_be_called_like_a_function_and_call_it(self, uut):
        uut.expect_call(1, 2, 3).will_once(Return(123))
        with satisfied(uut):
            assert uut(1, 2, 3) == 123

    def test_if_magic_method_does_not_have_expectation_set_and_does_not_exist_in_base_class_then_issue_uninterested_call_instead(
        self, uut, assert_that
    ):
        with pytest.raises(exc.UninterestedCall) as excinfo:
            math.floor(uut)
        actual_call = excinfo.value.actual_call
        assert actual_call.name == "uut.__floor__"
        assert_that.call_params_match(actual_call)  # called without params

    def test_if_magic_method_does_not_have_expectation_set_and_exists_in_base_class_then_call_existing_implementation(
        self, uut
    ):
        uut_hash = hash(uut)
        assert isinstance(uut_hash, int)

    def test_expect_equals_to_operator_to_be_used_and_use_it(self, uut):
        uut.__eq__.expect_call(123).will_once(Return(True))
        with satisfied(uut):
            assert uut == 123

    def test_expect_not_equals_to_operator_to_be_used_and_use_it(self, uut):
        uut.__ne__.expect_call(123).will_once(Return(True))
        with satisfied(uut):
            assert uut != 123

    def test_expect_less_than_operator_to_be_used_and_use_it(self, uut):
        uut.__lt__.expect_call(123).will_once(Return(True))
        with satisfied(uut):
            assert uut < 123

    def test_expect_greater_than_operator_to_be_used_and_use_it(self, uut):
        uut.__gt__.expect_call(123).will_once(Return(True))
        with satisfied(uut):
            assert uut > 123

    def test_expect_greater_or_equal_operator_to_be_used_and_use_it(self, uut):
        uut.__ge__.expect_call(123).will_once(Return(True))
        with satisfied(uut):
            assert uut >= 123

    def test_expect_less_or_equal_operator_to_be_used_and_use_it(self, uut):
        uut.__le__.expect_call(123).will_once(Return(True))
        with satisfied(uut):
            assert uut <= 123

    def test_expect_unary_pos_to_be_used_and_use_it(self, uut):
        uut.__pos__.expect_call().will_once(Return(1))
        with satisfied(uut):
            assert +uut == 1

    def test_expect_unary_neg_to_be_used_and_use_it(self, uut):
        uut.__neg__.expect_call().will_once(Return(-1))
        with satisfied(uut):
            assert -uut == -1

    def test_expect_abs_to_be_called_on_mock_and_call_it(self, uut):
        uut.__abs__.expect_call().will_once(Return(123))
        with satisfied(uut):
            assert abs(uut) == 123

    def test_expect_invert_to_be_called_on_mock_and_call_it(self, uut):
        uut.__invert__.expect_call().will_once(Return(123))
        with satisfied(uut):
            assert ~uut == 123

    def test_expect_round_to_be_called_without_args_and_call_it_without_args(self, uut):
        uut.__round__.expect_call().will_once(Return(123))
        with satisfied(uut):
            assert round(uut) == 123

    def test_expect_round_to_be_called_with_args_and_call_it_with_args(self, uut):
        uut.__round__.expect_call(2).will_once(Return(123))
        with satisfied(uut):
            assert round(uut, 2) == 123

    def test_expect_floor_to_be_called_on_mock_and_call_it(self, uut):
        uut.__floor__.expect_call().will_once(Return(123))
        with satisfied(uut):
            assert math.floor(uut) == 123

    def test_expect_ceil_to_be_called_on_mock_and_call_it(self, uut):
        uut.__ceil__.expect_call().will_once(Return(123))
        with satisfied(uut):
            assert math.ceil(uut) == 123

    def test_expect_trunc_to_be_called_on_mock_and_call_it(self, uut):
        uut.__trunc__.expect_call().will_once(Return(123))
        with satisfied(uut):
            assert math.trunc(uut) == 123

    def test_expect_add_to_be_called_and_call_it(self, uut):
        uut.__add__.expect_call(1).will_once(Return(3))
        with satisfied(uut):
            assert uut + 1 == 3

    def test_expect_sub_to_be_called_and_call_it(self, uut):
        uut.__sub__.expect_call(1).will_once(Return(1))
        with satisfied(uut):
            assert uut - 1 == 1

    def test_expect_mul_to_be_called_and_call_it(self, uut):
        uut.__mul__.expect_call(2).will_once(Return(4))
        with satisfied(uut):
            assert uut * 2 == 4

    def test_expect_floordiv_to_be_called_and_call_it(self, uut):
        uut.__floordiv__.expect_call(2).will_once(Return(2))
        with satisfied(uut):
            assert uut // 2 == 2

    def test_expect_truediv_to_be_called_and_call_it(self, uut):
        uut.__truediv__.expect_call(2).will_once(Return(2.5))
        with satisfied(uut):
            assert uut / 2 == 2.5

    def test_expect_mod_to_be_called_and_call_it(self, uut):
        uut.__mod__.expect_call(3).will_once(Return(2))
        with satisfied(uut):
            assert uut % 3 == 2

    def test_expect_divmod_to_be_called_and_call_it(self, uut):
        uut.__divmod__.expect_call(3).will_once(Return((2, 0)))
        with satisfied(uut):
            assert divmod(uut, 3) == (2, 0)

    def test_expect_pow_to_be_called_and_call_it(self, uut):
        uut.__pow__.expect_call(2).will_once(Return(16))
        with satisfied(uut):
            assert uut**2 == 16

    def test_expect_lshift_to_be_called_and_call_it(self, uut):
        uut.__lshift__.expect_call(2).will_once(Return(16))
        with satisfied(uut):
            assert uut << 2 == 16

    def test_expect_rshift_to_be_called_and_call_it(self, uut):
        uut.__rshift__.expect_call(2).will_once(Return(16))
        with satisfied(uut):
            assert uut >> 2 == 16

    def test_expect_and_to_be_called_and_call_it(self, uut):
        uut.__and__.expect_call(2).will_once(Return(16))
        with satisfied(uut):
            assert uut & 2 == 16

    def test_expect_or_to_be_called_and_call_it(self, uut):
        uut.__or__.expect_call(2).will_once(Return(16))
        with satisfied(uut):
            assert uut | 2 == 16

    def test_expect_xor_to_be_called_and_call_it(self, uut):
        uut.__xor__.expect_call(2).will_once(Return(16))
        with satisfied(uut):
            assert uut ^ 2 == 16

    def test_expect_radd_to_be_called_and_call_it(self, uut):
        uut.__radd__.expect_call(1).will_once(Return(3))
        with satisfied(uut):
            assert 1 + uut == 3

    def test_expect_rsub_to_be_called_and_call_it(self, uut):
        uut.__rsub__.expect_call(1).will_once(Return(1))
        with satisfied(uut):
            assert 1 - uut == 1

    def test_expect_rmul_to_be_called_and_call_it(self, uut):
        uut.__rmul__.expect_call(2).will_once(Return(4))
        with satisfied(uut):
            assert 2 * uut == 4

    def test_expect_rfloordiv_to_be_called_and_call_it(self, uut):
        uut.__rfloordiv__.expect_call(2).will_once(Return(2))
        with satisfied(uut):
            assert 2 // uut == 2

    def test_expect_rtruediv_to_be_called_and_call_it(self, uut):
        uut.__rtruediv__.expect_call(2).will_once(Return(2.5))
        with satisfied(uut):
            assert 2 / uut == 2.5

    def test_expect_rmod_to_be_called_and_call_it(self, uut):
        uut.__rmod__.expect_call(3).will_once(Return(2))
        with satisfied(uut):
            assert 3 % uut == 2

    def test_expect_rdivmod_to_be_called_and_call_it(self, uut):
        uut.__rdivmod__.expect_call(3).will_once(Return((2, 0)))
        with satisfied(uut):
            assert divmod(3, uut) == (2, 0)

    def test_expect_rpow_to_be_called_and_call_it(self, uut):
        uut.__rpow__.expect_call(2).will_once(Return(16))
        with satisfied(uut):
            assert 2**uut == 16

    def test_expect_rlshift_to_be_called_and_call_it(self, uut):
        uut.__rlshift__.expect_call(2).will_once(Return(16))
        with satisfied(uut):
            assert 2 << uut == 16

    def test_expect_rrshift_to_be_called_and_call_it(self, uut):
        uut.__rrshift__.expect_call(2).will_once(Return(16))
        with satisfied(uut):
            assert 2 >> uut == 16

    def test_expect_rand_to_be_called_and_call_it(self, uut):
        uut.__rand__.expect_call(2).will_once(Return(16))
        with satisfied(uut):
            assert 2 & uut == 16

    def test_expect_ror_to_be_called_and_call_it(self, uut):
        uut.__ror__.expect_call(2).will_once(Return(16))
        with satisfied(uut):
            assert 2 | uut == 16

    def test_expect_rxor_to_be_called_and_call_it(self, uut):
        uut.__rxor__.expect_call(2).will_once(Return(16))
        with satisfied(uut):
            assert 2 ^ uut == 16

    def test_expect_iadd_to_be_called_and_call_it(self, uut):
        uut.__iadd__.expect_call(1)
        with satisfied(uut):
            uut += 1

    def test_expect_isub_to_be_called_and_call_it(self, uut):
        uut.__isub__.expect_call(1)
        with satisfied(uut):
            uut -= 1

    def test_expect_imul_to_be_called_and_call_it(self, uut):
        uut.__imul__.expect_call(2)
        with satisfied(uut):
            uut *= 2

    def test_expect_ifloordiv_to_be_called_and_call_it(self, uut):
        uut.__ifloordiv__.expect_call(2)
        with satisfied(uut):
            uut //= 2

    def test_expect_itruediv_to_be_called_and_call_it(self, uut):
        uut.__itruediv__.expect_call(2)
        with satisfied(uut):
            uut /= 2

    def test_expect_imod_to_be_called_and_call_it(self, uut):
        uut.__imod__.expect_call(3)
        with satisfied(uut):
            uut %= 3

    def test_expect_ipow_to_be_called_and_call_it(self, uut):
        uut.__ipow__.expect_call(2)
        with satisfied(uut):
            uut **= 2

    def test_expect_ilshift_to_be_called_and_call_it(self, uut):
        uut.__ilshift__.expect_call(2)
        with satisfied(uut):
            uut <<= 2

    def test_expect_irshift_to_be_called_and_call_it(self, uut):
        uut.__irshift__.expect_call(2)
        with satisfied(uut):
            uut >>= 2

    def test_expect_iand_to_be_called_and_call_it(self, uut):
        uut.__iand__.expect_call(2)
        with satisfied(uut):
            uut &= 2

    def test_expect_ior_to_be_called_and_call_it(self, uut):
        uut.__ior__.expect_call(2)
        with satisfied(uut):
            uut |= 2

    def test_expect_ixor_to_be_called_and_call_it(self, uut):
        uut.__ixor__.expect_call(2)
        with satisfied(uut):
            uut ^= 2

    def test_when_expectation_is_recorded_on_div_magic_method_then_it_is_equivalent_to_recording_on_truediv_magic_method(
        self, uut
    ):
        uut.__div__.expect_call(2).will_once(Return(2.5))
        with satisfied(uut):
            assert uut / 2 == 2.5

    def test_when_expectation_is_recorded_on_rdiv_magic_method_then_it_is_equivalent_to_recording_on_rtruediv_magic_method(
        self, uut
    ):
        uut.__rdiv__.expect_call(2).will_once(Return(2.5))
        with satisfied(uut):
            assert 2 / uut == 2.5

    def test_when_expectation_is_recorded_on_idiv_magic_method_then_it_is_equivalent_to_recording_on_itruediv_magic_method(
        self, uut
    ):
        uut.__idiv__.expect_call(2)
        with satisfied(uut):
            uut /= 2

    def test_expect_int_conversion_to_be_called_and_call_it(self, uut):
        uut.__int__.expect_call().will_once(Return(3))
        with satisfied(uut):
            assert int(uut) == 3

    def test_expect_float_conversion_to_be_called_and_call_it(self, uut):
        uut.__float__.expect_call().will_once(Return(3.14))
        with satisfied(uut):
            assert float(uut) == 3.14

    def test_expect_complex_conversion_to_be_called_and_call_it(self, uut):
        uut.__complex__.expect_call().will_once(Return(complex(1, 2)))
        with satisfied(uut):
            assert complex(uut) == complex(1, 2)

    def test_expect_bool_conversion_to_be_called_and_call_it(self, uut):
        uut.__bool__.expect_call().will_once(Return(False))
        with satisfied(uut):
            assert not uut

    def test_expect_oct_conversion_to_be_called_and_call_it(self, uut):
        uut.__index__.expect_call().will_once(Return(8))
        with satisfied(uut):
            assert oct(uut) == "0o10"

    def test_expect_hex_conversion_to_be_called_and_call_it(self, uut):
        uut.__index__.expect_call().will_once(Return(8))
        with satisfied(uut):
            assert hex(uut) == "0x8"

    def test_expect_format_to_be_called_and_call_it(self, uut):
        uut.__format__.expect_call("abc").will_once(Return("World!"))
        with satisfied(uut):
            assert "Hello, {0:abc}".format(uut) == "Hello, World!"

    def test_expect_format_with_empty_params_to_be_called_and_call_it(self, uut):
        uut.__format__.expect_call("").will_once(Return("World!"))
        with satisfied(uut):
            assert "Hello, {}".format(uut) == "Hello, World!"

    def test_expect_dir_to_be_called_and_call_it(self, uut):
        uut.__dir__.expect_call().will_once(Return(["foo", "bar"]))
        with satisfied(uut):
            assert dir(uut) == ["bar", "foo"]

    def test_expect_hash_to_be_called_and_call_it(self, uut):
        uut.__hash__.expect_call().will_once(Return(123))
        with satisfied(uut):
            assert hash(uut) == 123

    def test_expect_sizeof_to_be_called_and_call_it(self, uut):
        uut.__sizeof__.expect_call().will_once(Return(32))
        with satisfied(uut):
            assert uut.__sizeof__() == 32

    def test_expect_str_call_and_then_call_str_on_mock(self, uut):
        uut.__str__.expect_call().will_once(Return("dummy"))
        with satisfied(uut):
            assert str(uut) == "dummy"

    def test_if_str_is_called_without_expectation_set_then_return_mocks_repr(self, uut):
        assert str(uut) == "<mockify.mock.Mock('uut')>"

    def test_expect_repr_call_and_call_it(self, uut):
        uut.__repr__.expect_call().will_once(Return("uut"))
        with satisfied(uut):
            assert repr(uut) == "uut"

    def test_if_repr_is_called_without_expectation_set_then_return_default_mock_repr(self, uut):
        assert repr(uut) == "<mockify.mock.Mock('uut')>"

    def test_expect_getattr_to_be_called_and_call_it(self, uut):
        uut.__getattr__.expect_call("foo").will_once(Return(123))
        with satisfied(uut):
            assert uut.foo == 123

    def test_expect_setattr_to_be_called_and_call_it(self, uut):
        uut.__setattr__.expect_call("foo", 123).times(1)
        with satisfied(uut):
            uut.foo = 123

    def test_expect_delattr_to_be_called_and_call_it(self, uut):
        uut.__delattr__.expect_call("foo").times(1)
        with satisfied(uut):
            del uut.foo

    def test_expect_len_to_be_called_and_call_it(self, uut):
        uut.__len__.expect_call().will_once(Return(123))
        with satisfied(uut):
            assert len(uut) == 123

    def test_expect_getitem_to_be_called_and_call_it(self, uut):
        uut.__getitem__.expect_call("foo").will_once(Return(123))
        with satisfied(uut):
            assert uut["foo"] == 123

    def test_expect_setitem_to_be_called_and_call_it(self, uut):
        uut.__setitem__.expect_call("foo", 123).times(1)
        with satisfied(uut):
            uut["foo"] = 123

    def test_expect_delitem_to_be_called_and_call_it(self, uut):
        uut.__delitem__.expect_call("foo").times(1)
        with satisfied(uut):
            del uut["foo"]

    def test_object_mock_allows_to_set_and_get_custom_properties(self, uut):
        uut.foo = 123
        assert uut.foo == 123
        del uut.foo

    def test_object_mock_allows_to_set_and_get_custom_items(self, uut):
        uut["foo"] = 123
        assert uut["foo"] == 123
        del uut["foo"]

    def test_object_mock_allows_to_set_and_get_both_items_and_attrs_allowing_name_reuse_for_different_purposes(
        self, uut
    ):
        uut.foo = 123
        uut["foo"] = "spam"
        assert uut.foo == 123
        assert uut["foo"] == "spam"

    def test_expect_reversed_to_be_called_and_call_it(self, uut):
        uut.__reversed__.expect_call().will_once(Return([1, 2, 3]))
        with satisfied(uut):
            assert reversed(uut) == [1, 2, 3]

    def test_expect_contains_to_be_called_and_call_it(self, uut):
        uut.__contains__.expect_call("foo").will_once(Return(True))
        uut.__contains__.expect_call("bar").will_once(Return(False))
        with satisfied(uut):
            assert "foo" in uut
            assert "bar" not in uut

    def test_expect_iter_to_be_called_and_call_it(self, uut):
        uut.__iter__.expect_call().will_repeatedly(Iterate([1, 2, 3])).times(2)
        with satisfied(uut):
            assert list(uut) == [1, 2, 3]
            assert list(iter(uut)) == [1, 2, 3]

    def test_expect_next_to_be_called_and_call_it(self, uut):
        uut.__next__.expect_call().will_once(Return(1)).will_once(Return(2))
        with satisfied(uut):
            assert next(uut) == 1
            assert next(uut) == 2

    def test_expect_generator_to_be_called_and_call_it(self, uut):

        def gen():
            for item in uut:
                yield item

        uut.__iter__.expect_call().will_once(Return(uut))
        uut.__next__.expect_call().will_once(Return(1)).will_once(Return(2)).will_once(Raise(StopIteration()))
        with satisfied(uut):
            assert list(gen()) == [1, 2]

    @pytest.mark.asyncio
    async def test_expect_async_generator_to_be_called_and_call_it(self, uut):

        async def gen():
            async for item in uut:
                yield item

        uut.__aiter__.expect_call().will_once(Return(uut))
        uut.__anext__.expect_call().will_once(Return(1)).will_once(Return(2)).will_once(Raise(StopAsyncIteration()))
        with satisfied(uut):
            assert [x async for x in gen()] == [1, 2]

    def test_when_call_is_expected_to_be_called_then_it_is_the_same_as_directly_expecting_mock_to_be_called(self, uut):
        uut.__call__.expect_call(1, 2).will_once(Return(3))
        with satisfied(uut):
            assert uut(1, 2) == 3

    def test_expect_context_enter_and_enter_context(self, uut):
        uut.__enter__.expect_call().will_once(Return(123))
        with satisfied(uut):
            with uut as foo:
                assert foo == 123

    def test_expect_context_exit_and_run_context_without_errors(self, uut):
        uut.__exit__.expect_call(None, None, None)
        with satisfied(uut):
            with uut:
                pass

    def test_expect_context_exit_and_run_context_with_raising_exception_that_is_handled(self, uut):
        uut.__exit__.expect_call(Type(type), Type(ValueError), _).will_once(Return(True))
        with satisfied(uut):
            with uut:
                raise ValueError("dummy")

    def test_expect_context_exit_and_run_context_with_raising_exception_that_is_passed_through(self, uut):
        uut.__exit__.expect_call(Type(type), Type(ValueError), _).will_once(Return(False))
        with satisfied(uut):
            with pytest.raises(ValueError):
                with uut:
                    raise ValueError("dummy")

    def test_when_context_having_no_expectations_is_left_with_exception_being_raised_then_pass_it_through(self, uut):
        with pytest.raises(ValueError):
            with uut:
                raise ValueError("dummy")

    @pytest.mark.asyncio
    async def test_expect_async_context_enter_and_enter_async_context(self, uut):
        uut.__aenter__.expect_call().will_once(Return(123))
        with satisfied(uut):
            async with uut as foo:
                assert foo == 123

    @pytest.mark.asyncio
    async def test_expect_async_context_exit_and_run_context_without_errors(self, uut):
        uut.__aexit__.expect_call(None, None, None)
        with satisfied(uut):
            async with uut:
                pass

    @pytest.mark.asyncio
    async def test_expect_async_context_exit_and_run_context_with_raising_exception_that_is_handled(self, uut):
        uut.__aexit__.expect_call(Type(type), Type(ValueError), _).will_once(Return(True))
        with satisfied(uut):
            async with uut:
                raise ValueError("dummy")

    @pytest.mark.asyncio
    async def test_expect_async_context_exit_and_run_context_with_raising_exception_that_is_passed_through(self, uut):
        uut.__aexit__.expect_call(Type(type), Type(ValueError), _).will_once(Return(False))
        with satisfied(uut):
            with pytest.raises(ValueError):
                async with uut:
                    raise ValueError("dummy")

    @pytest.mark.asyncio
    async def test_when_async_context_having_no_expectations_is_left_with_exception_being_raised_then_pass_it_through(
        self, uut
    ):
        with pytest.raises(ValueError):
            async with uut:
                raise ValueError("dummy")

    def test_dir_returns_user_defined_methods_and_properties_if_not_mocked(self, uut):
        assert dir(uut) == []
        uut.foo.expect_call()
        assert dir(uut) == ["foo"]
        uut.__enter__.expect_call()
        assert dir(uut) == ["__enter__", "foo"]
        uut.spam = 123
        assert dir(uut) == ["__enter__", "foo", "spam"]
        del uut.spam
        assert dir(uut) == ["__enter__", "foo"]
        uut.__getattr__.expect_call("bar")
        assert dir(uut) == ["__enter__", "__getattr__", "foo"]

    def test_expect_get_descriptor_to_be_called_via_instance_and_call_it(self, uut):

        class Dummy:
            foo = uut

        d = Dummy()

        uut.__get__.expect_call(d, Dummy).will_once(Return("spam"))
        with satisfied(uut):
            assert d.foo == "spam"

    def test_expect_get_descriptor_to_be_called_via_class_and_call_it(self, uut):

        class Dummy:
            foo = uut

        uut.__get__.expect_call(None, Dummy).will_once(Return("spam"))
        with satisfied(uut):
            assert Dummy.foo == "spam"

    def test_expect_set_descriptor_to_be_called_and_call_it(self, uut):

        class Dummy:
            foo = uut

        d = Dummy()

        uut.__set__.expect_call(d, 123)
        with satisfied(uut):
            d.foo = 123

    def test_expect_del_descriptor_to_be_called_and_call_it(self, uut):

        class Dummy:
            foo = uut

        d = Dummy()

        uut.__delete__.expect_call(d)
        with satisfied(uut):
            del d.foo

    def test_expect_call_method_can_also_be_expected_to_be_called(self, uut):
        uut.expect_call.expect_call(1, 2, 3)
        with satisfied(uut):
            uut.expect_call(1, 2, 3)

    def test_if_property_already_exists_then_recording_getattr_expectation_overrides_existing_value(self, uut):
        uut.foo = 123
        assert uut.foo == 123
        uut.__getattr__.expect_call("foo").will_once(Return("spam"))
        with satisfied(uut):
            assert uut.foo == "spam"

    def test_if_property_already_exists_then_recording_delattr_expectation_overrides_existing_value(self, uut):
        uut.foo = 123
        assert uut.foo == 123
        uut.__delattr__.expect_call("foo")
        with satisfied(uut):
            del uut.foo

    def test_if_property_already_exists_then_recording_setattr_expectation_overrides_existing_value(self, uut):
        uut.foo = 123
        assert uut.foo == 123
        uut.__setattr__.expect_call("foo", "spam")
        with satisfied(uut):
            uut.foo = "spam"

    def test_expect_mock_to_be_called_and_call_it(self, uut):
        uut.expect_call(1, 2).will_once(Return(3))
        with satisfied(uut):
            assert uut(1, 2) == 3

    def test_expect_method_to_be_called_and_call_that_method(self, uut):
        uut.foo.expect_call(1, 2).will_once(Return(3))
        with satisfied(uut):
            assert uut.foo(1, 2) == 3

    def test_when_depth_is_one_then_mocking_namespaced_methods_is_not_possible(self, uut):
        with pytest.raises(AttributeError) as excinfo:
            uut.foo.bar.expect_call()
        assert str(excinfo.value) == "'FunctionMock' object has no attribute 'bar'"


class TestMockWithMaxDepthSetToTwo:

    @pytest.fixture
    def uut(self):
        return Mock("uut", max_depth=2)

    def test_expect_mock_to_be_called_and_call_it(self, uut):
        uut.expect_call(1, 2).will_once(Return(3))
        with satisfied(uut):
            assert uut(1, 2) == 3

    def test_expect_method_to_be_called_and_call_that_method(self, uut):
        uut.foo.expect_call(1, 2).will_once(Return(3))
        with satisfied(uut):
            assert uut.foo(1, 2) == 3

    def test_expect_namespaced_method_to_be_called_and_call_that_method(self, uut):
        uut.foo.bar.expect_call(1, 2).will_once(Return(3))
        with satisfied(uut):
            assert uut.foo.bar(1, 2) == 3

    def test_when_depth_is_two_then_mocking_double_namespaced_methods_is_not_possible(self, uut):
        with pytest.raises(AttributeError) as excinfo:
            uut.foo.bar.baz.expect_call()
        assert str(excinfo.value) == "'FunctionMock' object has no attribute 'baz'"
