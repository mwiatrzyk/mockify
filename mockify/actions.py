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

import abc
import functools

from . import _utils


class Action(abc.ABC):
    """Common base class for all actions.

    .. versionadded:: 1.0

    Use this as a base for custom action classes.
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        formatted_params = _utils.format_args_kwargs(*self.args, **self.kwargs)
        return f"<{self.__module__}.{self.__class__.__name__}({formatted_params})>"

    def __eq__(self, other):
        return type(self) is type(other) and\
            self.args == other.args and\
            self.kwargs == other.kwargs

    def format_message(self):
        formatted_params = _utils.format_args_kwargs(*self.args, **self.kwargs)
        return f"{self.__class__.__name__}({formatted_params})"

    @abc.abstractmethod
    def __call__(self, actual_call):
        pass


class Return(Action):
    """Makes mock returning given value when called.

    :param value:
        Value to be returned
    """

    def __init__(self, value):
        super().__init__(value)

    def __call__(self, actual_call):
        return self.args[0]


class Iterate(Action):
    """Similar to :class:`Return`, but returns an iterator to given
    iterable.

    .. versionadded:: 1.0

    :param iterable:
        Value to be iterated
    """

    def __init__(self, iterable):
        super().__init__(iterable)

    def __call__(self, actual_call):
        return iter(self.args[0])


class Raise(Action):
    """Makes mock raising given exception when called.

    :param exc:
        Instance of exception to be raised
    """

    def __init__(self, exc):
        super().__init__(exc)

    def __call__(self, actual_call):
        raise self.args[0]


class Invoke(Action):
    """Allows to invoke custom function when mock is called.

    This is very handy if you want to do some sophisticated actions at the
    time when mock is called, but still checking how many times it was called
    and with what arguments.

    All arguments the mock was called with are passed to underlying function,
    and function's return value will be used as mock's return value.

    .. versionchanged:: 1.0
        Now this action allows binding args to function being called.

    :param func:
        Function to be executed

    :param args:
        Additional positional args to be bound to ``func``.

    :param kwargs:
        Additional named args to be bound to ``func``.
    """

    def __init__(self, func, *args, **kwargs):
        super().__init__(func, *args, **kwargs)
        self._func = functools.partial(func, *args, **kwargs)

    def __call__(self, actual_call):
        return self._func(*actual_call.args, **actual_call.kwargs)
