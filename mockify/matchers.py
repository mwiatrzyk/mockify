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


class Matcher(abc.ABC):
    """Abstract base class for matchers.

    .. versionchanged:: 1.0
        Now this inherits from :class:`abc.ABC`
    """

    @abc.abstractmethod
    def __repr__(self):
        """Return matcher's textual representation.

        Pay attention to this, as it is later used to render string
        representation of expected call parameters.
        """

    @abc.abstractmethod
    def __eq__(self, other):
        """Check if *other* can be accepted by this matcher."""

    def __ne__(self, other):
        return not self.__eq__(other)

    def __or__(self, other):
        return AnyOf(self, other)

    def __and__(self, other):
        return AllOf(self, other)


class AnyOf(Matcher):
    """Matches any value from given list of *values*.

    You can also use matchers in *values*.

    .. versionadded:: 1.0
    """

    def __init__(self, *values):
        self._values = values

    def __repr__(self):
        return '|'.join(repr(x) for x in self._values)

    def __eq__(self, other):
        for value in self._values:
            if value == other:
                return True
        else:
            return False


class AllOf(Matcher):
    """Matches if and only if received value is equal to all given
    *values*.

    You can also use matchers in *values*.

    .. versionadded:: 1.0
    """

    def __init__(self, *values):
        self._values = values

    def __repr__(self):
        return ' & '.join(repr(x) for x in self._values)

    def __eq__(self, other):
        for value in self._values:
            if value != other:
                return False
        else:
            return True


class Any(Matcher):
    """Matches any value.

    This can be used as a wildcard, when you care about number of arguments
    in your expectation, not their values or types. This can also be imported
    as underscore:

    .. testcode::

        from mockify.matchers import _
    """

    def __repr__(self):
        return "_"

    def __eq__(self, other):
        return True


class Type(Matcher):
    """Matches any value that is instance of one of given *types*.

    This is useful to record expectations where we do not care about expected
    value, but we do care about expected value type.

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
        return f"{self.__class__.__name__}({', '.join(x.__name__ for x in self._types)})"

    def __eq__(self, other):
        return isinstance(other, *self._types)


class Regex(Matcher):
    """Matches value if it is a string that matches given regular expression
    *pattern*.

    .. versionadded:: 1.0
    """

    def __init__(self, pattern):
        self._pattern = re.compile(pattern)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._pattern.pattern!r})"

    def __eq__(self, other):
        return isinstance(other, str) and\
            self._pattern.match(other) is not None


class Func(Matcher):
    """Matches value if *func* returns ``True`` for that value.

    This is the most generic matcher as you can use your own match function
    if needed.

    .. versionadded:: 1.0
    """

    def __init__(self, func):
        self._func = func

    def __repr__(self):
        return f"{self.__class__.__name__}({self._func!r})"

    def __eq__(self, other):
        return self._func(other)


_ = Any()
