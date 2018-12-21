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


class Return:
    """Used to record value a mock should return once called.

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
    """Used to record exception a mock should raise once called.

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
    """Used to trigger custom function once mock is called.

    When this is used, all positional and named arguments will be passed to
    ``func`` once mock is called, and ``func`` return value produced will be
    use as mock call return value.

    :param func:
        Function to be executed
    """

    def __init__(self, func):
        self._func = func

    def __str__(self):
        return "Invoke(<function {}>)".format(self._func.__name__)

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)
