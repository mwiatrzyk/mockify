# ---------------------------------------------------------------------------
# mockify/mock/_function.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import typing

from ..abc import IExpectation
from ..core import BaseMock, Call


class BaseFunctionMock(BaseMock):
    """Foundation class for making custom function mocks, with user-defined
    fixed set of positional and/or keyword arguments.

    Each subclass must provide pair of ``expect_call`` and ``__call__`` methods
    that will be used to record and consume (accordingly) expectations created
    with user-defined fixed set of arguments. Thanks to this class the linter
    will no longer complain about arguments that were redefined in subclass.

    For easier subclassing, this class provides two helper methods for easier
    implementing of ``__call__`` and ``expect_call`` methods:

        * :meth:`__m_call__`
        * :meth:`__m_expect_call__`

    Here's an example:

    .. testcode::

        from mockify.api import BaseFunctionMock, satisfied, Return

        class DummyFunctionMock(BaseFunctionMock):

            def __call__(self, a, b, c=None):
                return self.__m_call__(a, b, c=c)

            def expect_call(self, a, b, c=None):
                return self.__m_expect_call__(a, b, c=c)

        def call_func(func):
            return func(1, 2, c='spam')

        def test_call_func():
            mock = DummyFunctionMock('mock')
            mock.expect_call(1, 2, c='spam').will_once(Return(123))
            with satisfied(mock):
                assert call_func(mock) == 123

    .. testcode::
        :hide:

        test_call_func()

    .. versionadded:: (unreleased)
    """

    def __m_children__(self):
        """See :meth:`mockify.abc.IMock.__m_children__`."""
        return iter([])  # Function mock has no children

    def __m_expectations__(self):
        """See :meth:`mockify.abc.IMock.__m_expectations__`"""
        fullname = self.__m_fullname__
        return filter(
            lambda x: x.expected_call.name == fullname,
            self.__m_session__.expectations()
        )

    def __m_call__(self, *args, **kwargs):
        """A helper to implement ``__call__`` method in a subclass."""
        return self.__m_session__(Call(self.__m_fullname__, *args, **kwargs))

    def __m_expect_call__(self, *args, **kwargs) -> IExpectation:
        """A helper to implement ``expect_call`` method in a subclass."""
        return self.__m_session__.expect_call(
            Call(self.__m_fullname__, *args, **kwargs)
        )


class FunctionMock(BaseFunctionMock):
    """Class for mocking arbitrary Python functions.

    This is most basic mock class Mockify provides. You can use it to mock free
    Python functions (like callbacks), or to build more complex, custom mocks
    with it.

    Here's example usage:

    .. testcode::

        from mockify.api import satisfied, Return, FunctionMock

        def call_func(func):
            return func(1, 2, 3)

        def test_call_func():
            func = FunctionMock('func')
            func.expect_call(1, 2, 3).will_once(Return(123))
            with satisfied(func):
                assert call_func(func) == 123

    .. testcode::
        :hide:

        test_call_func()

    .. versionchanged:: 0.9
        Removed parameter ``session`` in favour of ``**kwargs``; session
        handling is now done by :class:`BaseMock` class.

    .. versionadded:: 0.8
    """

    def __call__(self, *args, **kwargs) -> typing.Optional[typing.Any]:
        """Call this mock."""
        return self.__m_call__(*args, **kwargs)

    def expect_call(self, *args, **kwargs) -> IExpectation:
        """Record call expectation on this mock."""
        return self.__m_expect_call__(*args, **kwargs)
