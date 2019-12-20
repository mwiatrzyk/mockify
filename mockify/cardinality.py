# ---------------------------------------------------------------------------
# mockify/cardinality.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
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

    .. versionadded:: 1.0

    This one is used to extract message formatting logic out of the
    :class:`mockify.Expectation` class. Now, all mock call count related
    classes reside in common module.
    """

    def __init__(self, initial_value):
        self._value = initial_value

    def __repr__(self):
        return repr(self._value)

    def __eq__(self, other):
        return self._value == other

    def __lt__(self, other):
        return self._value < other

    def __iadd__(self, other):
        self._value += other
        return self

    def format_message(self):
        """Return formatted textual representation of actual call count.

        This is used to render error messages.
        """
        if self._value == 0:
            return 'never called'
        else:
            return f"called {_utils.format_call_count(self._value)}"


class ExpectedCallCount(abc.ABC):
    """Abstract base class for classes used to set expected mock call count.

    .. versionadded:: 1.0
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

    @abc.abstractmethod
    def match(self, actual_call_count):
        """Check if *actual_call_count* matches expected call count.

        If actual call count matches expected call count, then return
        ``True``. Otherwise return ``False``.
        """
        return False

    @abc.abstractmethod
    def format_message(self):
        """Format message to be used in assertion reports.

        This message must state how many times the mock was expected to be
        called and will only be evaluated if expectation is not satisfied.
        """


class Exactly(ExpectedCallCount):
    """Used to expect fixed call count to be made.

    You do not have to use this class explicitly as its instances are
    automatically created when you call ``times`` method with integer value as
    argument.

    :param expected:
        Integer value representing expected call count
    """

    def __init__(self, expected):
        if expected < 0:
            raise TypeError("value of 'expected' must be >= 0")
        super().__init__(expected)

    @property
    def expected(self):
        return self.args[0]

    def match(self, actual_call_count):
        return self.expected == actual_call_count

    def format_message(self):
        if self.expected == 0:
            return 'to be never called'
        else:
            return f"to be called {_utils.format_call_count(self.expected)}"


class AtLeast(ExpectedCallCount):
    """Used to set minimal expected call count.

    If this is used, then expectation is said to be satisfied if actual call
    count is not less that ``minimal``.

    :param minimal:
        Integer value representing minimal expected call count
    """

    def __init__(self, minimal):
        if minimal < 0:
            raise TypeError("value of 'minimal' must be >= 0")
        super().__init__(minimal)

    @property
    def minimal(self):
        return self.args[0]

    def match(self, actual_call_count):
        return actual_call_count >= self.args[0]

    def format_message(self):
        if self.minimal == 0:
            return "to be called any number of times"
        else:
            return "to be called at least {}".format(_utils.format_call_count(self.minimal))


class AtMost(ExpectedCallCount):
    """Used to set maximal expected call count.

    If this is used, then expectation is said to be satisfied if actual call
    count is not greater than ``maximal``.

    :param maximal:
        Integer value representing maximal expected call count
    """

    def __new__(cls, maximal):
        if maximal < 0:
            raise TypeError("value of 'maximal' must be >= 0")
        elif maximal == 0:
            return Exactly(maximal)
        else:
            return super().__new__(cls)

    def __init__(self, maximal):
        super().__init__(maximal)

    @property
    def maximal(self):
        return self.args[0]

    def match(self, actual_call_count):
        return actual_call_count <= self.maximal

    def format_message(self):
        return "to be called at most {}".format(_utils.format_call_count(self.maximal))


class Between(ExpectedCallCount):
    """Used to set a range of valid call counts.

    If this is used, then expectation is said to be satisfied if actual call
    count is not less than ``minimal`` and not greater than ``maximal``.

    :param minimal:
        Integer value representing minimal expected call count

    :param maximal:
        Integer value representing maximal expected call count
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
        super().__init__(minimal, maximal)

    @property
    def minimal(self):
        return self.args[0]

    @property
    def maximal(self):
        return self.args[1]

    def match(self, actual_call_count):
        return actual_call_count >= self.minimal and\
            actual_call_count <= self.maximal

    def format_message(self):
        return f"to be called from {self.minimal} to {self.maximal} times"
