# ---------------------------------------------------------------------------
# mockify/core/_assert.py
#
# Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

# pylint: disable=missing-module-docstring

from .. import exc


def assert_satisfied(*mocks):
    """Check if all given mocks are **satisfied**.

    This function collects all expectations from given mock for which
    :meth:`Expectation.is_satisfied` evaluates to ``False``. Finally, if at
    least one **unsatisfied** expectation is found, this method raises
    :exc:`mockify.exc.Unsatisfied` exception.

    See :ref:`recording-and-validating-expectations` tutorial for more
    details.
    """

    def iter_unsatisfied_expectations(mocks):
        for mock in mocks:
            for child in mock.__m_walk__():
                yield from (
                    x for x in child.__m_expectations__()
                    if not x.is_satisfied()
                )

    unsatisfied_expectations = list(iter_unsatisfied_expectations(mocks))
    if unsatisfied_expectations:
        raise exc.Unsatisfied(unsatisfied_expectations)
