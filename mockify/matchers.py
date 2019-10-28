# ---------------------------------------------------------------------------
# mockify/matchers.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

"""Module containing predefined matchers.

A matcher is every class that inherits from :class:`Matcher` and implements
following methods:

    ``__repr__(self)``
        Return matcher's text representation.

    ``__eq__(self, other)``
        Check if ``self`` is *equal* to ``other``.

        Here we use standard Python ``__eq__`` operator as it will be
        automatically executed by Python no matter where the matcher is used.
        But *equality* definition is completely up to the matcher
        implementation.
"""

import re
import collections


class Matcher:
    """Base class for matchers."""

    def __ne__(self, other):
        return not self.__eq__(other)


class SaveArg(Matcher):
    """Matcher that matches any value and keeps ordered track of unique values.

    This can be used as a replacement for :class:`Any` in case that you need to
    ensure that mock was called in specified order.

    For example:

        >>> from _mockify.mock import Function
        >>> arg = SaveArg()
        >>> foo = Function('foo')
        >>> foo.expect_call(arg).times(3)
        <mockify.Expectation: foo(SaveArg)>
        >>> for i in range(3):
        ...     foo(i)
        >>> foo.assert_satisfied()
        >>> arg.called_with == [0, 1, 2]
        True
    """

    def __init__(self):
        self._called_with = []

    def __repr__(self):
        return self.__class__.__name__

    def __eq__(self, other):
        if not self._called_with:
            self._called_with.append(other)
        elif self._called_with[-1] != other:
            self._called_with.append(other)
        return True

    @property
    def called_with(self):
        """List of ordered unique values that this matcher was called with."""
        return list(self._called_with)


class Any(Matcher):
    """Matcher that matches any value.

    It is available also as ``_`` (underscore) single instance that can be
    imported from this module.

    For example, you can record expectation that mock must be called with one
    positional argument of any value but exactly 3 times:

        >>> from _mockify.matchers import _
        >>> from _mockify.mock import Function
        >>> foo = Function('foo')
        >>> foo.expect_call(_).times(3)
        <mockify.Expectation: foo(_)>
        >>> for i in range(3):
        ...     foo(i)
        >>> foo.assert_satisfied()
    """

    def __repr__(self):
        return "_"

    def __eq__(self, other):
        return True


class InstanceOf(Matcher):
    """A matcher that checks if given object is instance of one of given
    types.

    .. versionadded:: 0.6

    This is useful to record expectations where we do not care about expected
    value, but we care about expected value type.
    """

    def __init__(self, *types):
        self._types = types

    def __repr__(self):
        return f"InstanceOf({', '.join(repr(x) for x in self._types)})"

    def __eq__(self, other):
        return isinstance(other, *self._types)


class RegExp(Matcher):

    def __init__(self, pattern):
        self._pattern = re.compile(pattern)

    def __repr__(self):
        return f"RegExp({self._pattern.pattern!r})"

    def __eq__(self, other):
        return isinstance(other, str) and\
            self._pattern.match(other) is not None


_ = Any()
