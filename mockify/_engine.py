# ---------------------------------------------------------------------------
# mockify/_engine.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import os
import keyword
import weakref
import warnings
import itertools
import traceback
import collections
import unittest.mock

from contextlib import contextmanager

from . import exc, _utils



@contextmanager
def ordered(*mocks):
    """Preserve order in what expectations are defined.

    Use this to wrap test fragment in which you are recording expectations.
    All expectations recorded for listed mocks will be tracked and their
    order will be strictly checked during unit under test execution. If one
    expectation is called earlier than another, then execution will fail with
    an error.
    """

    def get_session():
        num_mocks = len(mocks)
        if num_mocks == 1:
            return mocks[0]._session
        for i in range(num_mocks-1):
            first, second = mocks[i], mocks[i+1]
            session = first._session
            if session is not second._session:
                raise TypeError(
                    f"Mocks {mocks[i]!r} and {mocks[i+1]!r} have to use same "
                    f"session object to make ordered expectations work.")
        else:
            return session

    session = get_session()
    session.enable_ordered(*map(lambda x: x._fullname, mocks))
    yield
    session.disable_ordered()


@contextmanager
def patched(*mocks):
    """Used to patch imported modules."""

    def having_expectations(*mocks):
        for mock in mocks:
            for mock in itertools.chain([mock], mock._children):
                if mock._expectations.count() > 0:
                    yield mock

    def patch_many(mocks):
        mock = next(mocks, None)
        if mock is None:
            yield
            return
        with unittest.mock.patch(mock._fullname, mock):
            yield from patch_many(mocks)

    for _ in patch_many(having_expectations(*mocks)):
        yield
        break


@contextmanager
def satisfied(*mocks):
    """Context manager for checking if given mocks are all satisfied when
    leaving the scope.

    It can be used with any mock and also with :class:`mockify.Registry`
    instances. The purpose of using this context manager is to emphasize the
    place in test code where given mocks are used.

    Here's an example test:

    .. testcode::

        from _mockify.mock import Function
        from _mockify.actions import Return

        class MockCaller:

            def __init__(self, mock):
                self._mock = mock

            def call_mock(self, a, b):
                return self._mock(a, b)

        def test_mock_caller():
            mock = Function('mock')

            mock.expect_call(1, 2).will_once(Return(3))

            uut = MockCaller(mock)
            with assert_satisfied(mock):
                assert uut.call_mock(1, 2) == 3

    .. testcleanup::

        test_mock_caller()
    """

    def unsatisfied_expectations(mock):
        for mock in itertools.chain([mock], mock._children):
            yield from mock._expectations.unsatisfied()

    yield
    unsatisfied_expectations =\
        itertools.chain(*map(lambda x: unsatisfied_expectations(x), mocks))
    unsatisfied_expectations = list(unsatisfied_expectations)
    if unsatisfied_expectations:
        raise exc.Unsatisfied(unsatisfied_expectations)
