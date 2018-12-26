# ---------------------------------------------------------------------------
# mockify/cardinality.py
#
# Copyright (C) 2018 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------

"""Module containing set of classes to be used with
:meth:`mockify.engine.Expectation.times` method.

You can also create your own classes to be used with that method. The only
thing required from such class is to implement following interface:

    ``is_satisfied(self, actual)``
        Return ``True`` if ``actual`` call count is satisfied by ``self``, or
        ``False`` otherwise.

        Here, ``actual`` is absolute call count expectation received so far. It
        is completely implementation-specific of which values of ``actual`` are
        said to be *satisfied* and which are not. For example, :class:`Exactly`
        will compare ``actual`` with fixed value (given via constructor) and
        return ``True`` only if those two are equal.

    ``adjust_by(self, minimal)``
        Adjust ``self`` by current ``minimal`` expected call count and return
        new instance of ``type(self)``.

        In some complex expectation there could be a situation in which
        expectation must be computed again. This is not visible for library
        user, but must be done behind the scenes to properly process
        expectations. Such situation can be presented in this example:

            >>> from mockify.actions import Return
            >>> from mockify.mock.function import Function
            >>> foo = Function('foo')
            >>> foo.expect_call(1, 2).will_once(Return(1)).will_repeatedly(Return(2)).times(2)
            <mockify.Expectation: foo(1, 2)>
            >>> foo(1, 2)
            1
            >>> foo(1, 2)
            2
            >>> foo(1, 2)
            2
            >>> foo.assert_satisfied()

        In example above we've used ``times(2)`` to tell that last repeated
        action is expected to be called twice, but real expected call count
        is 3 times, as ``will_once`` is used. Behind the scenes, this is
        recalculated using this metho.

    ``format_expected(self)``
        Return textual representation of expected call count.

        This is used by :class:`mockify.exc.Unsatisfied` exception when error
        message is being rendered.
"""

from mockify import _utils


class Exactly:
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
        self._expected = expected

    def is_satisfied(self, actual):
        return self._expected == actual

    def adjust_by(self, minimal):
        return self.__class__(self._expected + minimal)

    def format_expected(self):
        return _utils.format_expected_call_count(self._expected)


class AtLeast:
    """Used to set minimal expected call count.

    If this is used, then expectation is said to be satisfied if actual call
    count is not less that ``minimal``.

    :param minimal:
        Integer value representing minimal expected call count
    """

    def __init__(self, minimal):
        if minimal < 0:
            raise TypeError("value of 'minimal' must be >= 0")
        self._minimal = minimal

    def is_satisfied(self, actual):
        return actual >= self._minimal

    def adjust_by(self, minimal):
        return self.__class__(self._minimal + minimal)

    def format_expected(self):
        if self._minimal == 0:
            return "to be called optionally"
        else:
            return "to be called at least {}".format(_utils.format_call_count(self._minimal))


class AtMost:
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
        self._maximal = maximal

    def is_satisfied(self, actual):
        return actual <= self._maximal

    def adjust_by(self, minimal):
        return Between(minimal, self._maximal + minimal)

    def format_expected(self):
        return "to be called at most {}".format(_utils.format_call_count(self._maximal))


class Between:
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
        self._minimal = minimal
        self._maximal = maximal

    def is_satisfied(self, actual):
        return actual >= self._minimal and\
            actual <= self._maximal

    def adjust_by(self, minimal):
        return self.__class__(self._minimal + minimal, self._maximal + minimal)

    def format_expected(self):
        return "to be called between {} and {} times".format(self._minimal, self._maximal)
