# ---------------------------------------------------------------------------
# mockify/cardinality.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import abc

from functools import total_ordering

from . import _utils


@total_ordering
class ActualCallCount:
    """Proxy class that is used to calculate actual mock calls.

    Provides all needed arithmetic operators and a logic of rendering actual
    call message that is used in assertion messages.

    Here's an example:

        >>> from mockify.cardinality import ActualCallCount
        >>> str(ActualCallCount(0))
        'never called'
        >>> str(ActualCallCount(1))
        'called once'

    .. versionadded:: 1.0
    """

    def __init__(self, initial_value):
        self._value = initial_value

    def __repr__(self):
        return repr(self._value)

    def __str__(self):
        if self._value == 0:
            return 'never called'
        else:
            return f"called {_utils.format_call_count(self._value)}"

    def __eq__(self, other):
        return self._value == other

    def __lt__(self, other):
        return self._value < other

    def __iadd__(self, other):
        self._value += other
        return self


class ExpectedCallCount(abc.ABC):
    """Abstract base class for classes used to set expected call count on
    mock objects.

    .. versionadded:: 1.0
    """

    def __repr__(self):
        return f"<{self.__module__}.{self.__class__.__name__}({self.format_params()})>"

    def __eq__(self, other):
        return type(self) is type(other) and\
            self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    @abc.abstractmethod
    def __str__(self):
        """Format message to be used in assertion reports.

        This message must state how many times the mock was expected to be
        called and will only be evaluated if expectation is not satisfied.
        """

    @abc.abstractmethod
    def match(self, actual_call_count):
        """Check if *actual_call_count* matches expected call count."""

    @abc.abstractmethod
    def format_params(self, *args, **kwargs):
        """Format params to be used in **repr()**.

        This method must be overloaded without params, and call
        **super().format_params(...)** with args and kwargs you want to
        include in **repr()**.
        """
        return _utils.format_args_kwargs(*args, **kwargs)


class Exactly(ExpectedCallCount):
    """Used to set expected call count to fixed *expected* value.

    Expectations marked with this cardinality object will have to be called
    **exactly** *expected* number of times to be satisfied.

    You do not have to use this class explicitly as its instances are
    automatically created when you call :meth:`mockify.Expectation.times`
    method with integer value as argument.
    """

    def __init__(self, expected):
        if expected < 0:
            raise TypeError("value of 'expected' must be >= 0")
        self.expected = expected

    def __str__(self):
        if self.expected == 0:
            return 'to be never called'
        else:
            return f"to be called {_utils.format_call_count(self.expected)}"

    def match(self, actual_call_count):
        return self.expected == actual_call_count

    def format_params(self):
        return super().format_params(self.expected)


class AtLeast(ExpectedCallCount):
    """Used to set expected call count to given *minimal* value.

    Expectation will be satisfied if called not less times that given
    *minimal*.
    """

    def __init__(self, minimal):
        if minimal < 0:
            raise TypeError("value of 'minimal' must be >= 0")
        self.minimal = minimal

    def __str__(self):
        if self.minimal == 0:
            return "to be called any number of times"
        else:
            return "to be called at least {}".format(_utils.format_call_count(self.minimal))

    def match(self, actual_call_count):
        return actual_call_count >= self.minimal

    def format_params(self):
        return super().format_params(self.minimal)


class AtMost(ExpectedCallCount):
    """Used to set expected call count to given *maximal* value.

    If this is used, then expectation is said to be satisfied if actual call
    count is not greater than *maximal*.
    """

    def __new__(cls, maximal):
        if maximal < 0:
            raise TypeError("value of 'maximal' must be >= 0")
        elif maximal == 0:
            return Exactly(maximal)
        else:
            return super().__new__(cls)

    def __init__(self, maximal):
        self.maximal = maximal

    def __str__(self):
        return "to be called at most {}".format(_utils.format_call_count(self.maximal))

    def match(self, actual_call_count):
        return actual_call_count <= self.maximal

    def format_params(self):
        return super().format_params(self.maximal)


class Between(ExpectedCallCount):
    """Used to set a range of expected call counts between *minimal* and
    *maximal*, both included.

    If this is used, then expectation is said to be satisfied if actual call
    count is not less than *minimal* and not greater than *maximal*.
    """

    def __new__(cls, minimal, maximal):
        if minimal > maximal:
            raise TypeError("value of 'minimal' must not be greater than 'maximal'")
        elif minimal < 0:
            raise TypeError("value of 'minimal' must be >= 0")
        elif minimal == maximal:
            return Exactly(maximal)
        elif minimal == 0:
            return AtMost(maximal)
        else:
            return super().__new__(cls)

    def __init__(self, minimal, maximal):
        self.minimal = minimal
        self.maximal = maximal

    def __str__(self):
        return f"to be called from {self.minimal} to {self.maximal} times"

    def match(self, actual_call_count):
        return actual_call_count >= self.minimal and\
            actual_call_count <= self.maximal

    def format_params(self):
        return super().format_params(self.minimal, self.maximal)
