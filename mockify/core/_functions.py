# ---------------------------------------------------------------------------
# mockify/core/_functions.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

# pylint: disable=missing-module-docstring

import unittest.mock
from contextlib import contextmanager

from mockify import _utils, exc
from mockify.abc import IMock

__all__ = export = _utils.ExportList()


@export
def assert_satisfied(mock: IMock, *args: IMock):
    """Check if all given mocks are **satisfied**.

    This is done by collecting all :class:`mockify.abc.IExpectation` objects for
    which :meth:`mockify.abc.IExpectation.is_satisfied` returns ``False``.

    If there are unsatisfied expectations present, then
    :exc:`mockify.exc.Unsatisfied` exception is raised and list of found
    unsatisfied expectations is reported.

    :param mock:
        Mock object

    :param `*args`:
        Additional mock objects
    """

    def iter_unsatisfied_expectations(mocks):
        for mock in mocks:
            for child in mock.__m_walk__():
                yield from (
                    x for x in child.__m_expectations__()
                    if not x.is_satisfied()
                )

    def impl(*mocks):
        unsatisfied_expectations = list(iter_unsatisfied_expectations(mocks))
        if unsatisfied_expectations:
            raise exc.Unsatisfied(unsatisfied_expectations)

    impl(mock, *args)


@export
@contextmanager
def ordered(mock: IMock, *args: IMock):  # TODO: add more tests
    """Context manager that checks if expectations in wrapped scope are
    consumed in same order as they were defined.

    This context manager will raise :exc:`mockify.exc.UnexpectedCallOrder`
    assertion on first found mock that is executed out of specified order.

    See :ref:`Recording ordered expectations` for more details.

    :param mock:
        Mock object

    :param `*args`:
        Additional mock objects
    """

    def get_session(mocks):
        num_mocks = len(mocks)
        if num_mocks == 1:
            return mocks[0].__m_session__
        for i in range(num_mocks - 1):
            first, second = mocks[i], mocks[i + 1]
            session = first.__m_session__
            if session is not second.__m_session__:
                raise TypeError(
                    "Mocks {!r} and {!r} have to use same "
                    "session object".format(
                        first.__m_fullname__, second.__m_fullname__
                    )
                )
        return session

    def iter_expected_mock_names(mocks):
        for mock in mocks:
            for child in mock.__m_walk__():
                for expectation in child.__m_expectations__():
                    yield expectation.expected_call.name

    def impl(*mocks):
        session = get_session(mocks)
        session.enable_ordered(iter_expected_mock_names(mocks))
        yield
        session.disable_ordered()

    yield from impl(mock, *args)


@export
@contextmanager
def patched(mock: IMock, *args: IMock):
    """Context manager that replaces imported objects and functions with
    their mocks using mock name as a name of patched module.

    It will patch only functions or objects that have expectations recorded,
    so all needed expectations will have to be recorded before this context
    manager is used.

    See :ref:`Patching imported modules` for more details.

    :param mock:
        Mock object

    :param `*args`:
        Additional mock objects
    """

    def iter_mocks_with_expectations(mocks):
        for mock in mocks:
            for child in mock.__m_walk__():
                next_expectation = next(child.__m_expectations__(), None)
                if next_expectation is not None:
                    yield child

    def patch_many(mocks):
        mock = next(mocks, None)
        if mock is None:
            yield
        else:
            full_name = mock.__m_fullname__
            with unittest.mock.patch(full_name, mock):
                yield from patch_many(mocks)

    def impl(*mocks):
        for _ in patch_many(iter_mocks_with_expectations(mocks)):
            yield
            break

    yield from impl(mock, *args)


@export
@contextmanager
def satisfied(mock: IMock, *mocks: IMock):
    """Context manager wrapper for :func:`assert_satisfied`.

    :param mock:
        Mock object

    :param `*args`:
        Additional mock objects
    """
    yield
    assert_satisfied(mock, *mocks)
