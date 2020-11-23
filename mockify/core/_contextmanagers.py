# ---------------------------------------------------------------------------
# mockify/core/_contextmanagers.py
#
# Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

# pylint: disable=missing-module-docstring

import unittest.mock
from contextlib import contextmanager

from ._assert import assert_satisfied
from ._base_mock import MockInfo


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
            return mocks[0].__m_session__
        for i in range(num_mocks - 1):
            first, second = MockInfo(mocks[i]), MockInfo(mocks[i + 1])
            session = first.session
            if session is not second.session:
                raise TypeError(
                    "Mocks {!r} and {!r} have to use same "
                    "session object".format(
                        first.fullname, second.fullname
                    )
                )
        return session

    def iter_expected_mock_names(mocks):
        for mock in mocks:
            for child in MockInfo(mock).walk():
                for expectation in child.expectations():
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
            for child in MockInfo(mock).walk():
                next_expectation = next(child.expectations(), None)
                if next_expectation is not None:
                    yield child.target

    def patch_many(mocks):
        mock = next(mocks, None)
        if mock is None:
            yield
        else:
            full_name = MockInfo(mock).fullname
            with unittest.mock.patch(full_name, mock):
                yield from patch_many(mocks)

    for _ in patch_many(iter_mocks_with_expectations(mocks)):
        yield
        break


@contextmanager
def satisfied(*mocks):
    """Context manager wrapper for :func:`assert_satisfied`."""
    yield
    assert_satisfied(*mocks)
