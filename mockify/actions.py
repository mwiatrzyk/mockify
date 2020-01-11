# ---------------------------------------------------------------------------
# mockify/actions.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
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
    """Abstract base class for all actions.

    If you like to create your own action, you should inherit from this
    abstract class and implement all needed abstract methods. This class was
    added to force users to implement all needed methods and to provide
    implementation of common functionalities, like str(), repr() or
    (in)equality operators.

    .. versionadded:: 1.0
    """

    def __repr__(self):
        return f"<{self.__module__}.{self}>"

    def __str__(self):
        return f"{self.__class__.__name__}({self.format_params()})"

    def __eq__(self, other):
        return type(self) is type(other) and\
            self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    @abc.abstractmethod
    def __call__(self, actual_call):
        """Action body.

        It receives actual call object and returns action result based on
        that call object. This method may also raise exceptions if that is
        functionality of the action being implemented.

        :param actual_call:
            Object representing parameters of mock call being made
        """

    @abc.abstractmethod
    def format_params(self, *args, **kwargs):
        """Used to calculate str() and repr() for this action.

        This method should be overloaded in subclass without args, and then
        call super() with args and kwargs that are needed to be used in str()
        and repr() methods.
        """
        return _utils.format_args_kwargs(*args, **kwargs)


class Return(Action):
    """Makes mock returning given value when called.

    :param value:
        Value to be returned
    """

    def __init__(self, value):
        self.value = value

    def __call__(self, actual_call):
        return self.value

    def format_params(self):
        return super().format_params(self.value)


class Iterate(Action):
    """Similar to :class:`Return`, but returns an iterator to given
    iterable.

    .. versionadded:: 1.0

    :param iterable:
        Value to be iterated
    """

    def __init__(self, iterable):
        self.iterable = iterable

    def __call__(self, actual_call):
        return iter(self.iterable)

    def format_params(self):
        return super().format_params(self.iterable)


class Raise(Action):
    """Makes mock raising given exception when called.

    :param exc:
        Instance of exception to be raised
    """

    def __init__(self, exc):
        self.exc = exc

    def __call__(self, actual_call):
        raise self.exc

    def format_params(self):
        return super().format_params(self.exc)


class Invoke(Action):
    """Makes mock invoking given custom function when called.

    This is very handy if you want to do some additional assertions on
    parameters the mock was called with or to do some extra stuff during mock
    call (like creating file or whatever you need). The function will receive
    all positional and named args the mock was called with (in unchanged
    way). If it then returns a value or raises exception, that value will
    also be returned (or exception raised) by mock being called.

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
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, actual_call):
        partial_func = functools.partial(self.func, *self.args, **self.kwargs)
        return partial_func(*actual_call.args, **actual_call.kwargs)

    def format_params(self):
        return super().format_params(self.func, *self.args, **self.kwargs)
