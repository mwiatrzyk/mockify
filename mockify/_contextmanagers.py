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


@contextmanager
def ordered(*mocks):
    """Preserve order in what expectations are defined.

    Use this to wrap part of test code in which you run your unit under test.
    This must be used after expectations are recorded.
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
                    f"Mocks {first.name!r} and {second.name!r} have to use same "
                    f"session object")
        else:
            return session

    def iter_expected_mock_names(mocks):
        for mock in mocks:
            expectations = list(MockInfo(mock).expectations)
            for expectation in expectations:
                yield expectation.expected_call.name

    session = get_session()
    session.enable_ordered(iter_expected_mock_names(mocks))
    yield
    session.disable_ordered()


@contextmanager
def patched(*mocks):
    """Used to patch imported modules."""

    def iter_mocks_with_expectations(mocks):
        for mock in mocks:
            for mock_info in MockInfo(mock).walk():
                next_expectation = next(mock_info.expectations, None)
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
    """Used to wrap tested code in order to check if it satisfies given
    mocks."""

    def iter_unsatisfied_expectations(mocks):
        for mock in mocks:
            for mock_info in MockInfo(mock).walk():
                yield from (x for x in mock_info.expectations if not x.is_satisfied())

    yield
    unsatisfied_expectations = list(iter_unsatisfied_expectations(mocks))
    if unsatisfied_expectations:
        raise exc.Unsatisfied(unsatisfied_expectations)
