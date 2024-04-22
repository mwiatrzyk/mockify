# ---------------------------------------------------------------------------
# mockify/cardinality.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
"""Module containing types to be used to set expected number of mock
calls."""

import abc
from functools import total_ordering

from mockify import _utils
from mockify.abc import IExpectedCallCountMatcher

__all__ = export = _utils.ExportList()  # pylint: disable=invalid-all-format


def _format_repr(obj, *args, **kwargs):
    formatted_args_kwargs = _utils.ArgsKwargsFormatter().format(*args, **kwargs)
    return "<{}.{}({})>".format(obj.__module__, obj.__class__.__name__, formatted_args_kwargs)


@export
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

    .. versionadded:: 0.6
    """

    def __init__(self, initial_value):
        self._value = initial_value

    def __repr__(self):
        return repr(self._value)

    def __str__(self):
        if self._value == 0:
            return "never called"
        return "called {}".format(_utils.format_call_count(self._value))

    def __eq__(self, other):
        return self._value == other

    def __lt__(self, other):
        return self._value < other

    def __iadd__(self, other):
        self._value += other
        return self

    @property
    def value(self):
        """Number of actual mock calls."""
        return self._value


@export
class ExpectedCallCount(IExpectedCallCountMatcher, _utils.DictEqualityMixin):
    """Abstract base class for classes used to set expected call count on
    mock objects.

    .. versionadded:: 0.6
    """

    @abc.abstractmethod
    def __repr__(self):
        """Return textual representation of expected call count object.

        Since :meth:`__str__` is used to render textual message of expected
        call count, this should render actual object representation, i.e.
        module, name, params it was created with etc.

        .. versionchanged:: 0.11
            Now this is made abstract and previous :meth:`format_params` was
            removed.
        """

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
    def adjust_minimal(self, minimal):
        """Make a new cardinality object based on its current state and given
        *minimal*.

        This produces a new :class:`ExpectedCallCount` instance, but taking
        into account that some restrictions are already specified, f.e. with
        use of :meth:`Session.will_once`.
        """


@export
class Exactly(ExpectedCallCount):
    """Used to set expected call count to fixed *expected* value.

    Expectations marked with this cardinality object will have to be called
    **exactly** *expected* number of times to be satisfied.

    You do not have to use this class explicitly as its instances are
    automatically created when you call :meth:`mockify.core.Expectation.times`
    method with integer value as argument.
    """

    def __init__(self, expected):
        if expected < 0:
            raise TypeError("value of 'expected' must be >= 0")
        self.expected = expected

    def __repr__(self):
        return _format_repr(self, self.expected)

    def __str__(self):
        if self.expected == 0:
            return "to be never called"
        return "to be called {}".format(_utils.format_call_count(self.expected))

    def match(self, actual_call_count):
        return self.expected == actual_call_count

    def adjust_minimal(self, minimal):
        return Exactly(self.expected + minimal)


@export
class AtLeast(ExpectedCallCount):
    """Used to set expected call count to given *minimal* value.

    Expectation will be satisfied if called not less times that given
    *minimal*.
    """

    def __init__(self, minimal):
        if minimal < 0:
            raise TypeError("value of 'minimal' must be >= 0")
        self.minimal = minimal

    def __repr__(self):
        return _format_repr(self, self.minimal)

    def __str__(self):
        if self.minimal == 0:
            return "to be called any number of times"
        return "to be called at least {}".format(_utils.format_call_count(self.minimal))

    def match(self, actual_call_count):
        return actual_call_count >= self.minimal

    def adjust_minimal(self, minimal):
        return AtLeast(self.minimal + minimal)


@export
class AtMost(ExpectedCallCount):
    """Used to set expected call count to given *maximal* value.

    If this is used, then expectation is said to be satisfied if actual call
    count is not greater than *maximal*.
    """

    def __new__(cls, maximal):
        if maximal < 0:
            raise TypeError("value of 'maximal' must be >= 0")
        if maximal == 0:
            return Exactly(maximal)
        return super().__new__(cls)

    def __init__(self, maximal):
        self.maximal = maximal

    def __repr__(self):
        return _format_repr(self, self.maximal)

    def __str__(self):
        return "to be called at most {}".format(_utils.format_call_count(self.maximal))

    def match(self, actual_call_count):
        return actual_call_count <= self.maximal

    def adjust_minimal(self, minimal):
        return Between(minimal, self.maximal + minimal)


@export
class Between(ExpectedCallCount):
    """Used to set a range of expected call counts between *minimal* and
    *maximal*, both included.

    If this is used, then expectation is said to be satisfied if actual call
    count is not less than *minimal* and not greater than *maximal*.
    """

    def __new__(cls, minimal, maximal):
        if minimal > maximal:
            raise TypeError("value of 'minimal' must not be greater than 'maximal'")
        if minimal < 0:
            raise TypeError("value of 'minimal' must be >= 0")
        if minimal == maximal:
            return Exactly(maximal)
        if minimal == 0:
            return AtMost(maximal)
        return super().__new__(cls)

    def __init__(self, minimal, maximal):
        self.minimal = minimal
        self.maximal = maximal

    def __repr__(self):
        return _format_repr(self, self.minimal, self.maximal)

    def __str__(self):
        return "to be called from {} to {} times".format(self.minimal, self.maximal)

    def match(self, actual_call_count):
        return self.minimal <= actual_call_count <= self.maximal

    def adjust_minimal(self, minimal):
        return Between(self.minimal + minimal, self.maximal + minimal)
