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
    """Abstract base class for actions.

    This is common base class for all actions defined in this module. Custom
    actions should also inherit from this one.

    .. versionadded:: 0.6
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
            Instance of :class:`mockify.Call` containing params of actual
            call being made
        """

    @abc.abstractmethod
    def format_params(self, *args, **kwargs):
        """Used to calculate **str()** and **repr()** for this action.

        This method should be overloaded in subclass as a no argument method,
        and then call **super().format_params(...)** with args and kwargs
        you want to be included in **str()** and **repr()** methods.
        """
        return _utils.format_args_kwargs(args, kwargs)


class Return(Action):
    """Forces mock to return *value* when called.

    For example:

    .. doctest::

        >>> from mockify.mock import Mock
        >>> from mockify.actions import Return
        >>> mock = Mock('mock')
        >>> mock.expect_call().will_once(Return('foo'))
        <mockify.Expectation: mock()>
        >>> mock()
        'foo'
    """

    def __init__(self, value):
        self.value = value

    def __call__(self, actual_call):
        return self.value

    def format_params(self):
        return super().format_params(self.value)


class Iterate(Action):
    """Similar to :class:`Return`, but returns an iterator to given
    *iterable*.

    For example:

    .. doctest::

        >>> from mockify.mock import Mock
        >>> from mockify.actions import Iterate
        >>> mock = Mock('mock')
        >>> mock.expect_call().will_once(Iterate('foo'))
        <mockify.Expectation: mock()>
        >>> next(mock())
        'f'

    .. versionadded:: 0.6
    """

    def __init__(self, iterable):
        self.iterable = iterable

    def __call__(self, actual_call):
        return iter(self.iterable)

    def format_params(self):
        return super().format_params(self.iterable)


class Raise(Action):
    """Forces mock to raise *exc* when called.

    For example:

    .. doctest::

        >>> from mockify.mock import Mock
        >>> from mockify.actions import Raise
        >>> mock = Mock('mock')
        >>> mock.expect_call().will_once(Raise(ValueError('invalid value')))
        <mockify.Expectation: mock()>
        >>> mock()
        Traceback (most recent call last):
            ...
        ValueError: invalid value
    """

    def __init__(self, exc):
        self.exc = exc

    def __call__(self, actual_call):
        raise self.exc

    def format_params(self):
        return super().format_params(self.exc)


class Invoke(Action):
    """Forces mock to invoke *func* when called.

    When *func* is called, it is called with all bound arguments plus all
    arguments mock was called with. Value that mock returns is the one *func*
    returns. Use this action when more sophisticated checks have to be done
    when mock gets called or when your mock must operate on some **output
    parameter**.

    See :ref:`func-with-out-params` for more details.

    Here's an example using one of built-in functions as a *func*:

    .. doctest::

        >>> from mockify.mock import Mock
        >>> from mockify.actions import Invoke
        >>> mock = Mock('mock')
        >>> mock.expect_call([1, 2, 3]).will_once(Invoke(sum))
        <mockify.Expectation: mock([1, 2, 3])>
        >>> mock([1, 2, 3])
        6

    .. versionchanged:: 0.6
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
