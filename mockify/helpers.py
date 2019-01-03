# ---------------------------------------------------------------------------
# mockify/helpers.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------

from contextlib import contextmanager


@contextmanager
def assert_satisfied(*subjects):
    """Context manager for verifying multiple subjects at once.

    Each passed subject must have ``assert_satisfied`` method defined, so it
    can be used with :class:`mockify.mock.function.Function` or
    :class:`mockify.engine.Registry` instances for example.

    Basically, the role of this helper is to ensure that all subjects become
    satisfied after leaving wrapped context. For example:

        >>> from mockify.mock.function import Function
        >>> foo = Function('foo')
        >>> bar = Function('bar')
        >>> foo.expect_call()
        <mockify.Expectation: foo()>
        >>> bar.expect_call().times(0)
        <mockify.Expectation: bar()>
        >>> with assert_satisfied(foo, bar):
        ...     foo()

    And that's it - you don't have to explicitly check if ``foo`` and ``bar``
    are satisfied, because the helper will do it for you. And also it
    emphasizes part of code that actually uses given mocks.
    """
    yield
    for subject in subjects:
        subject.assert_satisfied()
