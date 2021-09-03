# ---------------------------------------------------------------------------
# mockify/mock/_mock.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
from typing import Callable, Dict

from .. import _utils
from ..core import BaseMock, Call, MockInfo
from ._object import ObjectMock


class Mock:
    """General purpose mock class.

    This class is used to:

    * create mocks of functions,
    * create mocks of objects with methods, setters and getters,
    * create mocks of modules,
    * create ad-hoc data objects.

    No matter what you will be mocking, for all cases creating mock objects
    is always the same - by giving it a *name* and optionally *session*. Mock
    objects automatically create attributes on demand, and that attributes
    form some kind of **nested** or **child** mocks.

    To record expectations, you have to call **expect_call()** method on one
    of that attributes, or on mock object itself (for function mocks). Then
    you pass mock object to unit under test. Finally, you will need
    :func:`mockify.core.assert_satisfied` function or :func:`mockify.core.satisfied`
    context manager to check if the mock is satisfied.

    Here's an example:

    .. testcode::

        from mockify.core import satisfied
        from mockify.mock import Mock

        def caller(func, a, b):
            func(a + b)

        def test_caller():
            func = Mock('func')
            func.expect_call(5)
            with satisfied(func):
                caller(func, 2, 3)

    .. testcode::
        :hide:

        test_caller()

    See :ref:`creating-mocks` for more details.

    .. versionchanged:: 0.8
        Now this class inherits from :class:`mockify.mock.BaseMock`

    .. versionadded:: 0.6
    """

    def __new__(cls, *args, **kwargs):
        kwargs['max_depth'] = -1
        return ObjectMock(*args, **kwargs)
