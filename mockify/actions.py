# ---------------------------------------------------------------------------
# mockify/actions.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

"""Module containing predefined actions that can be used as argument for
:meth:`Expectation.will_once` or :meth:`Expectation.will_repeatedly`.

Basically, any class containing following methods is considered an **action**:

    ``__str__(self)``

        Returning string representation of an action.

        This is used for error reporting.

    ``__call__(self, *args, **kwargs)``

        Method that is called when mock is called.

        Entire action logic goes in here.
"""

import functools


class Return:
    """Makes mock returning given value when called.

    :param value:
        Value to be returned
    """

    def __init__(self, value):
        self._value = value

    def __str__(self):
        return "Return({!r})".format(self._value)

    def __call__(self, *args, **kwargs):
        return self._value


class Iterate:
    """Similar to :class:`Return`, but returns an iterator to given
    iterable.

    .. versionadded:: 0.6

    :param iterable:
        Value to be iterated
    """

    def __init__(self, iterable):
        self._iterable = iterable

    def __str__(self):
        return f"Iterate({self._iterable!r})"

    def __call__(self, call):
        return iter(self._iterable)


class Raise:
    """Makes mock raising given exception when called.

    :param exc:
        Instance of exception to be raised
    """

    def __init__(self, exc):
        self._exc = exc

    def __str__(self):
        return "Raise({!r})".format(self._exc)

    def __call__(self, *args, **kwargs):
        raise self._exc


class Invoke:
    """Makes mock invoking given function when called.

    When mock is called, all arguments (if there are any) are passed to the
    ``func`` and its return value is returned as mock's return value.

    :param func:
        Function to be executed
    """

    def __init__(self, func, *args, **kwargs):
        self._func = functools.partial(func, *args, **kwargs)

    def __str__(self):
        return f"Invoke({self._func.func!r})"

    def __call__(self, actual_call):
        return self._func(*actual_call.args, **actual_call.kwargs)
