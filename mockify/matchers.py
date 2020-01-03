# ---------------------------------------------------------------------------
# mockify/matchers.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import re
import abc
import collections


class Matcher(abc.ABC):
    """Abstract base class for matchers.

    .. versionchanged:: 1.0
        Now this inherits from :class:`abc.ABC`
    """

    @abc.abstractmethod
    def __repr__(self):
        pass

    @abc.abstractmethod
    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __or__(self, other):
        return Alt(self, other)


class Alt(Matcher):
    """A matcher that can match against set of other matchers.

    If a value matches to at least one matcher, then match is found.

    .. versionadded:: 1.0
    """

    def __init__(self, *matchers):
        self._matchers = matchers

    def __repr__(self):
        return '|'.join(repr(x) for x in self._matchers)

    def __eq__(self, other):
        for matcher in self._matchers:
            if matcher == other:
                return True
        else:
            return False


class Any(Matcher):
    """Matcher that matches any value.

    This can be used as a wildcard, when you care about number of arguments
    in your expectation, not their values or types.
    """

    def __repr__(self):
        return "_"

    def __eq__(self, other):
        return True


class Type(Matcher):
    """A matcher that checks if given object is instance of one of given
    types.

    This is useful to record expectations where we do not care about expected
    value, but we care about expected value type.

    .. versionadded:: 1.0
    """

    def __init__(self, *types):
        if not types:
            raise TypeError("__init__() requires at least 1 positional argument, got 0")
        self.__validate_types(types)
        self._types = types

    def __validate_types(self, types):
        for type_ in types:
            if not isinstance(type_, type):
                raise TypeError(f"__init__() requires type instances, got {type_!r}")

    def __repr__(self):
        return f"Type({', '.join(x.__name__ for x in self._types)})"

    def __eq__(self, other):
        return isinstance(other, *self._types)


class Value(Matcher):
    """A matcher that can match any of given fixed values.

    .. versionadded:: 1.0
    """

    def __init__(self, *values):
        if not values:
            raise TypeError('__init__() requires at least 1 positional argument, got 0')
        self._values = values

    def __repr__(self):
        return f"Value({', '.join(repr(x) for x in self._values)})"

    def __eq__(self, other):
        return other in self._values


class Regex(Matcher):
    """A matcher that will match string values that match given regular
    expression pattern.

    .. versionadded:: 1.0
    """

    def __init__(self, pattern):
        self._pattern = re.compile(pattern)

    def __repr__(self):
        return f"Regex({self._pattern.pattern!r})"

    def __eq__(self, other):
        return isinstance(other, str) and\
            self._pattern.match(other) is not None


_ = Any()
