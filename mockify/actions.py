# ---------------------------------------------------------------------------
# mockify/actions.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
"""Module containing action types.

Actions are used to tell the mock what it must do once called with given set
of arguments. This can be returning a value, returning a generator, calling a
function, raising exception etc.
"""

import abc
import functools
import inspect
from contextlib import contextmanager

from . import _utils


def _format_str(obj, *args, **kwargs):
    return "{}({})".format(
        obj.__class__.__name__,
        _utils.ArgsKwargsFormatter().format(*args, **kwargs)
    )


class Action(abc.ABC, _utils.DictEqualityMixin):
    """Abstract base class for actions.

    This is common base class for all actions defined in this module. Custom
    actions should also inherit from this one.

    .. versionadded:: 0.6
    """

    def __repr__(self):
        return "<{}.{}>".format(self.__module__, self)

    @abc.abstractmethod
    def __str__(self):
        """Return string representation of this action.

        This is later used in error messages when test fails.

        .. versionchanged:: 0.11
            Now this is made abstract and previous abstract
            :meth:`format_params` was removed
        """

    @abc.abstractmethod
    def __call__(self, actual_call):
        """Action body.

        It receives actual call object and returns action result based on
        that call object. This method may also raise exceptions if that is
        functionality of the action being implemented.

        :param actual_call:
            Instance of :class:`mockify.core.Call` containing params of actual
            call being made
        """


class Return(Action):
    """Forces mock to return *value* when called.

    For example:

    .. doctest::

        >>> from mockify.mock import Mock
        >>> from mockify.actions import Return
        >>> mock = Mock('mock')
        >>> mock.expect_call().will_once(Return('foo'))
        <mockify.Expectation: mock()>
        >>> mock()
        'foo'
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return _format_str(self, self.value)

    def __call__(self, actual_call):
        return self.value


class ReturnAsync(Return):
    """Similar to :class:`Return`, but to be used with asynchronous Python
    code.

    For example:

    .. testcode::

        from mockify.core import satisfied
        from mockify.mock import Mock
        from mockify.actions import ReturnAsync

        async def async_caller(func):
            return await func()

        async def test_async_caller():
            func = Mock('func')
            func.expect_call().will_once(ReturnAsync('foo'))
            with satisfied(func):
                assert await async_caller(func) == 'foo'

    .. testcode::
        :hide:

        from mockify._compat import asyncio
        asyncio.run(test_async_caller())

    .. versionadded:: 0.11
    """

    def __call__(self, actual_call):

        async def proxy(value):
            return value

        return proxy(self.value)


class ReturnContext(Return):
    """Similar to :class:`Return`, but returns *value* via context
    manager.

    For example:

    .. testcode::

        from mockify.core import satisfied
        from mockify.mock import MockFactory
        from mockify.actions import Return, ReturnContext

        class UserStorage:

            def __init__(self, database):
                self._database = database

            def get(self, user_id):
                with self._database.begin_transaction() as transaction:
                    return transaction.users.get(user_id)

        def test_user_storage_get():
            factory = MockFactory()
            transaction = factory.mock('transaction')
            transaction.users.get.expect_call(123).will_once(Return('user-123'))
            database = factory.mock('database')
            database.begin_transaction.expect_call().will_once(ReturnContext(transaction))
            with satisfied(factory):
                assert UserStorage(database).get(123) == 'user-123'

    .. testcode::
        :hide:

        test_user_storage_get()

    .. versionadded:: 0.12
    """

    def __call__(self, actual_call):

        @contextmanager
        def proxy(value):
            yield value

        return proxy(self.value)


class ReturnAsyncContext(ReturnContext):
    """Similar to :class:`ReturnContext`, but returns *value* via async
    context manager.

    For example:

    .. testcode::

        from mockify.core import satisfied
        from mockify.mock import MockFactory
        from mockify.actions import Return, ReturnAsyncContext

        class UserStorage:

            def __init__(self, database):
                self._database = database

            async def get(self, user_id):
                async with self._database.begin_transaction() as transaction:
                    return await transaction.users.get(user_id)

        async def test_user_storage_async_get():
            factory = MockFactory()
            transaction = factory.mock('transaction')
            transaction.users.get.expect_call(123).will_once(ReturnAsync('user-123'))
            database = factory.mock('database')
            database.begin_transaction.expect_call().will_once(ReturnAsyncContext(transaction))
            with satisfied(factory):
                assert await UserStorage(database).get(123) == 'user-123'

    .. testcode::
        :hide:

        from mockify._compat import asyncio
        asyncio.run(test_user_storage_async_get())

    .. versionadded:: 0.12
    """

    def __call__(self, actual_call):

        class Proxy:

            def __init__(self, value):
                self._value = value

            async def __aenter__(self):
                return self._value

            async def __aexit__(self, exc_type, exc_value, traceback):
                pass

        return Proxy(self.value)


class Iterate(Action):
    """Similar to :class:`Return`, but returns an iterator to given
    *iterable*.

    For example:

    .. doctest::

        >>> from mockify.mock import Mock
        >>> from mockify.actions import Iterate
        >>> mock = Mock('mock')
        >>> mock.expect_call().will_once(Iterate('foo'))
        <mockify.Expectation: mock()>
        >>> next(mock())
        'f'

    .. versionadded:: 0.6
    """

    def __init__(self, iterable):
        self.iterable = iterable

    def __str__(self):
        return _format_str(self, self.iterable)

    def __call__(self, actual_call):
        return iter(self.iterable)


class IterateAsync(Iterate):
    """Similar to :class:`Iterate`, but returns awaitable that returns an
    iterator to given *iterable*.

    For example:

    .. testcode::

        from mockify.core import satisfied
        from mockify.mock import Mock
        from mockify.actions import IterateAsync

        async def get_next(func):
            iterable = await func()
            return next(iterable)

        async def test_get_next():
            func = Mock('func')
            func.expect_call().will_once(IterateAsync('foo'))
            with satisfied(func):
                assert await get_next(func) == 'f'

    .. testcode::
        :hide:

        from mockify._compat import asyncio
        asyncio.run(test_get_next())

    .. versionadded:: 0.11
    """

    def __call__(self, actual_call):

        async def proxy(iterable):
            return iter(iterable)

        return proxy(self.iterable)


class YieldAsync(Iterate):
    """Similar to :class:`Iterate`, but returns async iterator to given *iterable*.

    This iterator can later be used with ``async for`` statement.

    For example:

    .. testcode::

        from mockify.core import satisfied
        from mockify.mock import Mock
        from mockify.actions import YieldAsync

        async def fetch(func):
            result = []
            async for item in func():
                result.append(item)
            return result

        async def test_fetch():
            func = Mock('func')
            func.expect_call().will_once(YieldAsync('foo'))
            with satisfied(func):
                assert await fetch(func) == ['f', 'o', 'o']

    .. testcode::
        :hide:

        from mockify._compat import asyncio
        asyncio.run(test_fetch())

    .. versionadded:: 0.12
    """

    def __call__(self, actual_call):

        async def proxy(iterable):
            for item in iterable:
                yield item

        return proxy(self.iterable)


class Raise(Action):
    """Forces mock to raise *exc* when called.

    For example:

    .. doctest::

        >>> from mockify.mock import Mock
        >>> from mockify.actions import Raise
        >>> mock = Mock('mock')
        >>> mock.expect_call().will_once(Raise(ValueError('invalid value')))
        <mockify.Expectation: mock()>
        >>> mock()
        Traceback (most recent call last):
            ...
        ValueError: invalid value
    """

    def __init__(self, exc):
        self.exc = exc

    def __str__(self):
        return _format_str(self, self.exc)

    def __call__(self, actual_call):
        raise self.exc


class RaiseAsync(Raise):
    """Similar to :class:`Raise`, but to be used with asynchronous Python
    code.

    For example:

    .. testcode::

        from mockify.core import satisfied
        from mockify.mock import Mock
        from mockify.actions import RaiseAsync

        async def async_caller(func):
            try:
                return await func()
            except ValueError as e:
                return str(e)

        async def test_async_caller():
            func = Mock('func')
            func.expect_call().will_once(RaiseAsync(ValueError('an error')))
            with satisfied(func):
                assert await async_caller(func) == 'an error'

    .. testcode::
        :hide:

        from mockify._compat import asyncio
        asyncio.run(test_async_caller())

    .. versionadded:: 0.11
    """

    def __call__(self, actual_call):

        async def proxy(exc):
            raise exc

        return proxy(self.exc)


class Invoke(Action):
    """Forces mock to invoke *func* when called.

    When *func* is called, it is called with all bound arguments plus all
    arguments mock was called with. Value that mock returns is the one *func*
    returns. Use this action when more sophisticated checks have to be done
    when mock gets called or when your mock must operate on some **output
    parameter**.

    See :ref:`func-with-out-params` for more details.

    Here's an example using one of built-in functions as a *func*:

    .. doctest::

        >>> from mockify.mock import Mock
        >>> from mockify.actions import Invoke
        >>> mock = Mock('mock')
        >>> mock.expect_call([1, 2, 3]).will_once(Invoke(sum))
        <mockify.Expectation: mock([1, 2, 3])>
        >>> mock([1, 2, 3])
        6

    .. versionchanged:: 0.6
        Now this action allows binding args to function being called.

    :param func:
        Function to be executed

    :param args:
        Additional positional args to be bound to ``func``.

    :param kwargs:
        Additional named args to be bound to ``func``.
    """

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    @property
    def _bound_func(self):
        return functools.partial(self.func, *self.args, **self.kwargs)

    def __str__(self):
        return _format_str(self, self.func, *self.args, **self.kwargs)

    def __call__(self, actual_call):
        return self._bound_func(*actual_call.args, **actual_call.kwargs)


class InvokeAsync(Invoke):
    """Similar to :class:`Invoke`, but to be used with asynchronous Python
    code.

    This action can be instantiated with either non-async or async *func*. No
    matter which one you pick, it always makes mock awaitable. Here's an
    example showing usage with both callback function types:

    .. testcode::

        from mockify.core import satisfied
        from mockify.mock import Mock
        from mockify.actions import InvokeAsync
        from mockify.matchers import _

        async def test_invoke_async_with_non_async_func():

            def func(numbers):
                return sum(numbers)

            mock = Mock('func')
            mock.expect_call(_).will_once(InvokeAsync(func))
            with satisfied(mock):
                assert await mock([1, 2, 3]) == 6

        async def test_invoke_async_with_async_func():

            async def async_func(numbers):
                return sum(numbers)

            mock = Mock('func')
            mock.expect_call(_).will_once(InvokeAsync(async_func))
            with satisfied(mock):
                assert await mock([1, 2, 3]) == 6

    .. testcode::
        :hide:

        from mockify._compat import asyncio
        asyncio.run(test_invoke_async_with_non_async_func())
        asyncio.run(test_invoke_async_with_async_func())

    .. versionadded:: 0.11
    """

    def __call__(self, actual_call):

        async def proxy(func, actual_call):
            if inspect.iscoroutinefunction(func.func):
                return await func(*actual_call.args, **actual_call.kwargs)
            return func(*actual_call.args, **actual_call.kwargs)

        return proxy(self._bound_func, actual_call)
