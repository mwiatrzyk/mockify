# ---------------------------------------------------------------------------
# mockify/_contextmanagers.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import itertools
import unittest.mock

from contextlib import contextmanager

from . import exc
from .mock import MockInfo
from ._assert import assert_satisfied


@contextmanager
def ordered(*mocks):  # TODO: add more tests
    """Context manager that checks if expectations in wrapped scope are
    consumed in same order as they were defined.

    This context manager will raise :exc:`mockify.exc.UnexpectedCallOrder`
    assertion on first found mock that is executed out of specified order.

    See :ref:`Recording ordered expectations` for more details.
    """

    def get_session():
        num_mocks = len(mocks)
        if num_mocks == 1:
            return mocks[0]._session
        for i in range(num_mocks-1):
            first, second = mocks[i], mocks[i+1]
            session = first._session
            if session is not second._session:
                first, second = MockInfo(mocks[i]), MockInfo(mocks[i+1])
                raise TypeError(
                    "Mocks {!r} and {!r} have to use same "
                    "session object".format(first.name, second.name))
        else:
            return session

    def iter_expected_mock_names(mocks):
        for mock in mocks:
            for mock_info in MockInfo(mock).walk():
                for expectation in mock_info.expectations():
                    yield expectation.expected_call.name

    session = get_session()
    session.enable_ordered(iter_expected_mock_names(mocks))
    yield
    session.disable_ordered()


@contextmanager
def patched(*mocks):
    """Context manager that replaces imported objects and functions with
    their mocks using mock name as a name of patched module.

    It will patch only functions or objects that have expectations recorded,
    so all needed expectations will have to be recorded before this context
    manager is used.

    See :ref:`Patching imported modules` for more details.
    """

    def iter_mocks_with_expectations(mocks):
        for mock in mocks:
            for mock_info in MockInfo(mock).walk():
                next_expectation = next(mock_info.expectations(), None)
                if next_expectation is not None:
                    yield mock_info.mock

    def patch_many(mocks):
        mock = next(mocks, None)
        if mock is None:
            yield
        else:
            mock_name = MockInfo(mock).name
            with unittest.mock.patch(mock_name, mock):
                yield from patch_many(mocks)

    for _ in patch_many(iter_mocks_with_expectations(mocks)):
        yield
        break


@contextmanager
def satisfied(*mocks):
    """Context manager wrapper for :func:`assert_satisfied`."""
    yield
    assert_satisfied(*mocks)
