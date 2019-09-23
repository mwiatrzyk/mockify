# ---------------------------------------------------------------------------
# mockify/mock/_function.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

from .. import _utils, Call, Context


class Function:
    """Class for mocking Python functions.

    This is the most basic mocking class and as such it is internally used by
    other mock classes. But of course you can use it directly to mock things
    like callbacks, comparators, key function etc.

    :param name:
        Function mock name

    :param ctx:
        Instance of :class:`mockify.Context` to be used.

        If not given, a default one will be created and used for this mock
        object.
    """

    def __init__(self, name, ctx=None):
        self._name = name
        self._ctx = ctx or Context()

    def __repr__(self):
        return "<mockify.mock.{}({!r})>".format(self.__class__.__name__, self._name)

    def __call__(self, *args, **kwargs):
        """Call mock function."""
        actual_call = self._make_call(*args, **kwargs)
        return self._ctx(actual_call)

    def expect_call(self, *args, **kwargs):
        """Record call expectation on this function mock."""
        expected_call = self._make_call(*args, **kwargs)
        return self._ctx.expect_call(expected_call)

    def _make_call(self, *args, **kwargs):
        return Call(self._name, *args, **kwargs)
