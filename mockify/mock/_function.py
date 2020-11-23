# ---------------------------------------------------------------------------
# mockify/mock/_function.py
#
# Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

from ..core import BaseMock, Call, MockInfo


class FunctionMock(BaseMock):
    """Class for mocking Python functions.

    This is most basic mock class Mockify provides. It can be used as a
    standalone mock, for mocking standalone functions in tests, or to build
    more complex mocks.

    Here's example usage:

    .. testcode::

        from mockify.core import satisfied
        from mockify.mock import FunctionMock
        from mockify.actions import Return

        func = FunctionMock('func')
        func.expect_call(1, 2, 3).will_once(Return(123))
        with satisfied(func):
            assert func(1, 2, 3) == 123

    :param name:
        Name of mocked function.

        This must a valid Python identifier or series of valid Python
        identifiers concatenated with a period sign (f.e. ``foo.bar.baz``).

    .. versionchanged:: 0.9
        Removed parameter ``session`` in favour of ``**kwargs``; session
        handling is now done by :class:`BaseMock` class.

    .. versionadded:: 0.8
    """

    def __init__(self, name, **kwargs):
        super().__init__(name=name, **kwargs)

    @property
    def _info(self):
        return MockInfo(self)

    def __m_children__(self):
        return iter([])  # Function mock has no children

    def __m_expectations__(self):
        return filter(
            lambda x: x.expected_call.name == self._info.fullname,
            self.__m_session__.expectations()
        )

    def __call__(self, *args, **kwargs):
        return self.__m_session__(Call(self._info.fullname, *args, **kwargs))

    def expect_call(self, *args, **kwargs):
        return self.__m_session__.expect_call(
            Call(self._info.fullname, *args, **kwargs)
        )
