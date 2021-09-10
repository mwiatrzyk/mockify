# ---------------------------------------------------------------------------
# tests/unit/test_actions.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import pytest

from mockify.actions import (
    Invoke, InvokeAsync, Iterate, IterateAsync, Raise, RaiseAsync, Return,
    ReturnAsync, ReturnAsyncContext, ReturnContext, YieldAsync
)
from mockify.core import satisfied
from mockify.mock import Mock


class TestReturn:
    _str_test_data = [
        (123, 'Return(123)'),
        (3.14, 'Return(3.14)'),
        ('foo', "Return('foo')"),
    ]

    @pytest.mark.parametrize('value, expected_repr', _str_test_data)
    def test_repr(self, value, expected_repr):
        assert repr(Return(value)
                    ) == "<mockify.actions.{}>".format(expected_repr)

    @pytest.mark.parametrize('value, expected_str', _str_test_data)
    def test_str(self, value, expected_str):
        assert str(Return(value)) == expected_str

    def test_expect_mock_to_return_value_once(self):
        mock = Mock('mock')
        mock.expect_call().will_once(Return(1))
        with satisfied(mock):
            assert mock() == 1

    def test_expect_mock_to_return_two_values_in_given_order(self):
        mock = Mock('mock')
        mock.expect_call().will_once(Return(1)).will_once(Return(2))
        with satisfied(mock):
            assert mock() == 1
            assert mock() == 2

    def test_expect_mock_to_return_one_value_once_and_then_other_value_repeatedly(
        self
    ):
        mock = Mock('mock')
        mock.expect_call().will_once(Return(1)).will_repeatedly(Return(2))
        with satisfied(mock):
            assert mock() == 1
            for _ in range(2):
                assert mock() == 2


class TestReturnAsync:
    _str_test_data = [
        (123, 'ReturnAsync(123)'),
        (3.14, 'ReturnAsync(3.14)'),
        ('foo', "ReturnAsync('foo')"),
    ]

    @pytest.mark.parametrize('value, expected_repr', _str_test_data)
    def test_repr(self, value, expected_repr):
        assert repr(ReturnAsync(value)
                    ) == "<mockify.actions.{}>".format(expected_repr)

    @pytest.mark.parametrize('value, expected_str', _str_test_data)
    def test_str(self, value, expected_str):
        assert str(ReturnAsync(value)) == expected_str

    @pytest.mark.asyncio
    async def test_expect_mock_to_asynchronously_return_value_once(self):
        mock = Mock('mock')
        mock.expect_call().will_once(ReturnAsync(1))
        with satisfied(mock):
            assert await mock() == 1


class TestReturnContext:
    _str_test_data = [
        (123, 'ReturnContext(123)'),
        (3.14, 'ReturnContext(3.14)'),
        ('foo', "ReturnContext('foo')"),
    ]

    @pytest.mark.parametrize('value, expected_repr', _str_test_data)
    def test_repr(self, value, expected_repr):
        assert repr(ReturnContext(value)
                    ) == "<mockify.actions.{}>".format(expected_repr)

    @pytest.mark.parametrize('value, expected_str', _str_test_data)
    def test_str(self, value, expected_str):
        assert str(ReturnContext(value)) == expected_str

    def test_expect_mock_to_return_value_via_context_manager_when_called(self):
        mock = Mock('mock')
        mock.expect_call().will_once(ReturnContext(123))
        with satisfied(mock):
            with mock() as ctx:
                assert ctx == 123


class TestReturnAsyncContext:
    _str_test_data = [
        (123, 'ReturnAsyncContext(123)'),
        (3.14, 'ReturnAsyncContext(3.14)'),
        ('foo', "ReturnAsyncContext('foo')"),
    ]

    @pytest.mark.parametrize('value, expected_repr', _str_test_data)
    def test_repr(self, value, expected_repr):
        assert repr(ReturnAsyncContext(value)
                    ) == "<mockify.actions.{}>".format(expected_repr)

    @pytest.mark.parametrize('value, expected_str', _str_test_data)
    def test_str(self, value, expected_str):
        assert str(ReturnAsyncContext(value)) == expected_str

    @pytest.mark.asyncio
    async def test_expect_mock_to_return_value_via_async_context_manager_when_called(
        self
    ):
        mock = Mock('mock')
        mock.expect_call().will_once(ReturnAsyncContext(123))
        with satisfied(mock):
            async with mock() as ctx:
                assert ctx == 123


class TestIterate:
    _str_test_data = [
        ([], 'Iterate([])'),
        ('123', "Iterate('123')"),
    ]

    @pytest.mark.parametrize('value, expected_str', _str_test_data)
    def test_repr(self, value, expected_str):
        assert repr(Iterate(value)
                    ) == "<mockify.actions.{}>".format(expected_str)

    @pytest.mark.parametrize('value, expected_str', _str_test_data)
    def test_str(self, value, expected_str):
        assert str(Iterate(value)) == expected_str

    def test_expect_mock_to_iterate_over_sequence_once(self):
        mock = Mock('mock')
        mock.expect_call().will_once(Iterate('abc'))
        with satisfied(mock):
            assert list(mock()) == list('abc')

    def test_expect_mock_to_iterate_over_two_sequences_in_given_order(self):
        mock = Mock('mock')
        mock.expect_call().will_once(Iterate('abc')).will_once(Iterate('cde'))
        with satisfied(mock):
            assert list(mock()) == list('abc')
            assert list(mock()) == list('cde')

    def test_expect_mock_to_return_one_value_once_and_then_other_value_repeatedly(
        self
    ):
        mock = Mock('mock')
        mock.expect_call().will_once(Iterate('abc')
                                     ).will_repeatedly(Iterate('cde'))
        with satisfied(mock):
            assert list(mock()) == list('abc')
            for _ in range(2):
                assert list(mock()) == list('cde')


class TestIterateAsync:
    _str_test_data = [
        ([], 'IterateAsync([])'),
        ('123', "IterateAsync('123')"),
    ]

    @pytest.mark.parametrize('value, expected_str', _str_test_data)
    def test_repr(self, value, expected_str):
        assert repr(IterateAsync(value)
                    ) == "<mockify.actions.{}>".format(expected_str)

    @pytest.mark.parametrize('value, expected_str', _str_test_data)
    def test_str(self, value, expected_str):
        assert str(IterateAsync(value)) == expected_str

    @pytest.mark.asyncio
    async def test_expect_mock_to_iterate_over_sequence_once(self):
        mock = Mock('mock')
        mock.expect_call().will_once(IterateAsync('abc'))
        with satisfied(mock):
            assert list(await mock()) == list('abc')


class TestYieldAsync:
    _str_test_data = [
        (123, 'YieldAsync(123)'),
        (3.14, 'YieldAsync(3.14)'),
        ('foo', "YieldAsync('foo')"),
    ]

    @pytest.mark.parametrize('value, expected_repr', _str_test_data)
    def test_repr(self, value, expected_repr):
        assert repr(YieldAsync(value)
                    ) == "<mockify.actions.{}>".format(expected_repr)

    @pytest.mark.parametrize('value, expected_str', _str_test_data)
    def test_str(self, value, expected_str):
        assert str(YieldAsync(value)) == expected_str

    @pytest.mark.asyncio
    async def test_expect_mock_to_async_iterate_over_sequence_once(self):
        mock = Mock('mock')
        mock.expect_call().will_once(YieldAsync('abc'))
        with satisfied(mock):
            items = []
            async for item in mock():
                items.append(item)
            assert items == ['a', 'b', 'c']


class TestRaiseBase:

    class Error(Exception):

        def __init__(self, message):
            super().__init__()
            self.message = message

        def __repr__(self):
            return "Error({!r})".format(self.message)


class TestRaise(TestRaiseBase):
    _str_test_data = [
        (TestRaiseBase.Error('an error'), "Raise(Error('an error'))"),
    ]

    @pytest.mark.parametrize('value, expected_str', _str_test_data)
    def test_repr(self, value, expected_str):
        assert repr(Raise(value)) == "<mockify.actions.{}>".format(expected_str)

    @pytest.mark.parametrize('value, expected_str', _str_test_data)
    def test_str(self, value, expected_str):
        assert str(Raise(value)) == expected_str

    def test_expect_mock_to_raise_exception_once(self):
        mock = Mock('mock')
        mock.expect_call().will_once(Raise(ValueError('one')))
        with satisfied(mock):
            with pytest.raises(ValueError) as excinfo:
                mock()
            assert str(excinfo.value) == 'one'

    def test_expect_mock_to_raise_two_exceptions_in_given_order(self):
        first_exc, second_exc = ValueError('first'), ValueError('second')
        mock = Mock('mock')
        mock.expect_call().will_once(Raise(first_exc)
                                     ).will_once(Raise(second_exc))
        with satisfied(mock):
            with pytest.raises(ValueError) as first_excinfo:
                mock()
            with pytest.raises(ValueError) as second_excinfo:
                mock()
            assert str(first_excinfo.value) == 'first'
            assert str(second_excinfo.value) == 'second'

    def test_expect_mock_to_raise_one_exception_once_and_then_other_exception_repeatedly(
        self
    ):
        first_exc, second_exc = ValueError('first'), ValueError('second')
        mock = Mock('mock')
        mock.expect_call().will_once(Raise(first_exc)
                                     ).will_repeatedly(Raise(second_exc))
        with satisfied(mock):
            with pytest.raises(ValueError) as first_excinfo:
                mock()
            assert str(first_excinfo.value) == 'first'
            for _ in range(2):
                with pytest.raises(ValueError) as second_excinfo:
                    mock()
                assert str(second_excinfo.value) == 'second'


class TestRaiseAsync(TestRaiseBase):
    _str_test_data = [
        (TestRaiseBase.Error('an error'), "RaiseAsync(Error('an error'))"),
    ]

    @pytest.mark.parametrize('value, expected_str', _str_test_data)
    def test_repr(self, value, expected_str):
        assert repr(RaiseAsync(value)
                    ) == "<mockify.actions.{}>".format(expected_str)

    @pytest.mark.parametrize('value, expected_str', _str_test_data)
    def test_str(self, value, expected_str):
        assert str(RaiseAsync(value)) == expected_str

    @pytest.mark.asyncio
    async def test_expect_mock_to_asynchronously_return_value_once(self):
        mock = Mock('mock')
        mock.expect_call().will_once(RaiseAsync(ValueError('an error')))
        with satisfied(mock):
            with pytest.raises(ValueError) as excinfo:
                await mock()
            assert str(excinfo.value) == 'an error'


class TestInvoke:

    @pytest.fixture(autouse=True)
    def setup(self):

        def func(*args, **kwargs):
            self.called_with.append((args, kwargs))
            return sum(args)

        self.func = func
        self.called_with = []

    ### Tests

    def test_repr(self):
        action = Invoke(self.func)
        assert '<mockify.actions.Invoke(<function TestInvoke.setup.<locals>.func at 0x' in repr(
            action
        )

    def test_str(self):
        action = Invoke(self.func)
        assert 'Invoke(<function TestInvoke.setup.<locals>.func at 0x' in str(
            action
        )

    @pytest.mark.parametrize(
        'args, kwargs', [
            ((1, 2), {}),
            ((1, 2, 3), {
                'c': 4
            }),
        ]
    )
    def test_expect_mock_to_invoke_given_function_once(self, args, kwargs):
        mock = Mock('mock')
        mock.expect_call(*args, **kwargs).will_once(Invoke(self.func))
        with satisfied(mock):
            assert mock(*args, **kwargs) == sum(args)
            assert self.called_with == [(args, kwargs)]

    def test_when_bound_args_attached_to_function__then_call_it_with_bound_args_and_call_args(
        self
    ):
        mock = Mock('mock')
        mock.expect_call().will_once(Invoke(self.func, 1, 2, 3))
        with satisfied(mock):
            assert mock() == sum([1, 2, 3])
            assert self.called_with == [((1, 2, 3), {})]


class TestInvokeAsync:

    @pytest.fixture(autouse=True)
    def setup(self):

        def func(*args, **kwargs):
            self.func_args.append((args, kwargs))
            return sum(args)

        async def async_func(*args, **kwargs):
            self.async_func_args.append((args, kwargs))
            return sum(args)

        self.func = func
        self.async_func = async_func
        self.func_args = []
        self.async_func_args = []

    def test_repr(self):
        action = InvokeAsync(self.func)
        assert '<mockify.actions.InvokeAsync(<function TestInvokeAsync.setup.<locals>.func at 0x' in repr(
            action
        )

    def test_str(self):
        action = InvokeAsync(self.func)
        assert 'InvokeAsync(<function TestInvokeAsync.setup.<locals>.func at 0x' in str(
            action
        )

    @pytest.mark.asyncio
    async def test_invoke_mock_with_non_async_func_passed_to_invoke_async_action(
        self
    ):
        mock = Mock('mock')
        mock.expect_call(1, 2).will_once(InvokeAsync(self.func))
        with satisfied(mock):
            assert await mock(1, 2) == 3
        assert self.func_args == [((1, 2), {})]

    @pytest.mark.asyncio
    async def test_invoke_mock_with_non_async_func_passed_to_invoke_async_action_with_args(
        self
    ):
        mock = Mock('mock')
        mock.expect_call(3, 4).will_once(InvokeAsync(self.func, 1, 2, c=3))
        with satisfied(mock):
            assert await mock(3, 4) == 10
        assert self.func_args == [((1, 2, 3, 4), {'c': 3})]

    @pytest.mark.asyncio
    async def test_invoke_mock_with_async_func_passed_to_invoke_async_action(
        self
    ):
        mock = Mock('mock')
        mock.expect_call(1, 2).will_once(InvokeAsync(self.async_func))
        with satisfied(mock):
            assert await mock(1, 2) == 3
        assert self.async_func_args == [((1, 2), {})]

    @pytest.mark.asyncio
    async def test_invoke_mock_with_async_func_passed_to_invoke_async_action_with_args(
        self
    ):
        mock = Mock('mock')
        mock.expect_call(3,
                         4).will_once(InvokeAsync(self.async_func, 1, 2, c=3))
        with satisfied(mock):
            assert await mock(3, 4) == 10
        assert self.async_func_args == [((1, 2, 3, 4), {'c': 3})]
