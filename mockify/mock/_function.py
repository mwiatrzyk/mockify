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

from ..core import BaseMock, Call
from ..interface import IExpectation


class FunctionMock(BaseMock):
    """Class for mocking Python functions.

    This is most basic mock class Mockify provides. You can use it to mock free
    Python functions (like callbacks), or to build more complex, custom mocks
    with it.

    Here's example usage:

    .. testcode::

        from mockify.api import satisfied, Return, FunctionMock

        func = FunctionMock('func')
        func.expect_call(1, 2, 3).will_once(Return(123))
        with satisfied(func):
            assert func(1, 2, 3) == 123

    .. versionchanged:: 0.9
        Removed parameter ``session`` in favour of ``**kwargs``; session
        handling is now done by :class:`BaseMock` class.

    .. versionadded:: 0.8
    """

    def __m_children__(self):
        """See :meth:`mockify.interface.IMock.__m_children__`"""
        return iter([])  # Function mock has no children

    def __m_expectations__(self):
        """See :meth:`mockify.interface.IMock.__m_expectations__`"""
        fullname = self.__m_fullname__
        return filter(
            lambda x: x.expected_call.name == fullname,
            self.__m_session__.expectations()
        )

    def __call__(self, *args, **kwargs) -> typing.Optional[typing.Any]:
        """Call this mock."""
        return self.__m_session__(Call(self.__m_fullname__, *args, **kwargs))

    def expect_call(self, *args, **kwargs) -> IExpectation:
        """Record call expectation on this mock."""
        return self.__m_session__.expect_call(
            Call(self.__m_fullname__, *args, **kwargs)
        )
