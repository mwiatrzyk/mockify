# ---------------------------------------------------------------------------
# mockify/actions.py
#
# Copyright (C) 2018 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
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

    def __init__(self, func):
        self._func = func

    def __str__(self):
        return "Invoke(<function {}>)".format(self._func.__name__)

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)
