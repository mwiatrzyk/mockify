# ---------------------------------------------------------------------------
# mockify/matchers.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
"""Module with types representing matchers.

Matchers are used to wildcard some expected parameters when expectation is
recorded. Matchers do that by overloading (in)equality operator in their
specific way. With this you can record expectations using value ranges, type
checking, regular expressions and more.
"""

import abc
import re

from mockify import _utils

__all__ = export = _utils.ExportList(["_"])  # pylint: disable=invalid-all-format


def _format_repr(obj, *args, **kwargs):

    def skip_kwarg_func(value):
        return value is None

    formatted_args_kwargs = _utils.ArgsKwargsFormatter(sort=False, skip_kwarg_if=skip_kwarg_func).format(
        *args, **kwargs
    )
    return "{}({})".format(obj.__class__.__name__, formatted_args_kwargs)


@export
class Matcher(abc.ABC):
    """Abstract base class for matchers.

    .. versionchanged:: 0.6
        Now this inherits from :class:`abc.ABC`
    """

    @abc.abstractmethod
    def __eq__(self, other):
        """Check if *other* can be accepted by this matcher."""

    @abc.abstractmethod
    def __repr__(self):
        """Return textual representation of this matcher.

        Returned string representation is later used in error reporting.
        """

    def __ne__(self, other):
        return not self.__eq__(other)

    def __or__(self, other):
        return AnyOf(self, other)

    def __and__(self, other):
        return AllOf(self, other)


@export
class AnyOf(Matcher):
    """Matches any value from given list of *values*.

    You can also use matchers in *values*.

    .. versionadded:: 0.6
    """

    def __init__(self, *values):
        self._values = values

    def __eq__(self, other):
        for value in self._values:
            if value == other:
                return True
        return False

    def __repr__(self):
        return " | ".join(repr(x) for x in self._values)


@export
class AllOf(Matcher):
    """Matches if and only if received value is equal to all given
    *values*.

    You can also use matchers in *values*.

    .. versionadded:: 0.6
    """

    def __init__(self, *values):
        self._values = values

    def __eq__(self, other):
        for value in self._values:
            if value != other:
                return False
        return True

    def __repr__(self):
        return " & ".join(repr(x) for x in self._values)


@export
class Any(Matcher):
    """Matches any value.

    This can be used as a wildcard, when you care about number of arguments
    in your expectation, not their values or types.

    .. note::

        This is also available as ``_`` (underscore) member of
        :mod:`mockify.matchers` module:

        .. testcode::

            from mockify.matchers import _, Any

            assert isinstance(_, Any)
    """

    def __eq__(self, other):
        return True

    def __repr__(self):
        return "_"


_ = Any()


@export
class Type(Matcher):
    """Matches any value that is instance of one of given *types*.

    This is useful to record expectations where we do not care about expected
    value, but we do care about expected value type.

    .. versionadded:: 0.6
    """

    def __init__(self, *types):
        if not types:
            raise TypeError("__init__() requires at least 1 positional argument, got 0")
        self.__validate_types(types)
        self._types = types

    @staticmethod
    def __validate_types(types):
        for type_ in types:
            if not isinstance(type_, type):
                raise TypeError("__init__() requires type instances, got {!r}".format(type_))

    def __eq__(self, other):
        return isinstance(other, *self._types)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, ", ".join(x.__name__ for x in self._types))


@export
class Regex(Matcher):
    """Matches value if it is a string that matches given regular expression
    *pattern*.

    :param pattern:
        Regular expression pattern

    :param name:
        Optional name for given pattern.

        If given, then name will be used in text representation of this
        matcher. This can be very handy, especially when regular expression
        is complex and hard to read. Example:

        .. doctest::

            >>> r = Regex(r'^[a-z]+$', 'LOWER_ASCII')
            >>> repr(r)
            'Regex(LOWER_ASCII)'

    .. versionadded:: 0.6
    """

    def __init__(self, pattern, name=None):
        self._pattern = re.compile(pattern)
        self._name = name

    def __eq__(self, other):
        return isinstance(other, str) and self._pattern.match(other) is not None

    def __repr__(self):
        if self._name is None:
            return "{}({!r})".format(self.__class__.__name__, self._pattern.pattern)
        return "{}({})".format(self.__class__.__name__, self._name)


@export
class List(Matcher):
    """Matches value if it is a list of values matching *matcher*.

    :param matcher:
        A matcher that every value in the list is expected to match.

        Use :class:`Any` matcher if you want to match list containing any
        values.

    :param min_length:
        Minimal accepted list length

    :param max_length:
        Maximal accepted list length

    .. versionadded:: 0.6
    """

    def __init__(self, matcher, min_length=None, max_length=None):
        self._matcher = matcher
        self._min_length = min_length
        self._max_length = max_length

    def __eq__(self, other):
        if not isinstance(other, list):
            return False
        if self._max_length is not None and len(other) > self._max_length:
            return False
        if self._min_length is not None and len(other) < self._min_length:
            return False
        for item in other:
            if self._matcher != item:
                return False
        return True

    def __repr__(self):
        return _format_repr(self, self._matcher, min_length=self._min_length, max_length=self._max_length)


@export
class Object(Matcher):
    """Matches value if it is an object with attributes equal to names and
    values given via keyword args.

    This matcher creates ad-hoc object using provided keyword args. These
    args are then used to compare with value's attributes of same name. All
    attributes must match for this matcher to accept value.

    Here's an example:

    .. testcode::

        from collections import namedtuple

        from mockify.core import satisfied
        from mockify.mock import Mock
        from mockify.matchers import Object

        CallArg = namedtuple('CallArg', 'foo, bar')

        mock = Mock('mock')
        mock.expect_call(Object(foo=1, bar=2))

        with satisfied(mock):
            mock(CallArg(1, 2))

    .. versionadded:: 0.6.5

    :param ``**kwargs``:
        Arguments to compare value with
    """

    _undefined = object()

    def __init__(self, **kwargs):
        if not kwargs:
            raise TypeError("__init__ must be called with at least 1 named argument")
        self._kwargs = kwargs

    def __eq__(self, other):
        for key, value in self._kwargs.items():
            reference_value = getattr(other, key, self._undefined)
            if reference_value is self._undefined or value != reference_value:
                return False
        return True

    def __repr__(self):
        return _format_repr(self, **self._kwargs)


@export
class Func(Matcher):
    """Matches value if *func* returns ``True`` for that value.

    This is the most generic matcher as you can use your own match function
    if needed.

    :param func:
        Function to be used to calculate match.

    :param name:
        Optional name for this matcher.

        This can be used to set a name used to format matcher's text
        representation for assertion errors. Here's a simple example:

        .. doctest::

            >>> f = Func(lambda x: x > 0, 'POSITIVE_ONLY')
            >>> repr(f)
            'Func(POSITIVE_ONLY)'

    .. versionadded:: 0.6
    """

    def __init__(self, func, name=None):
        self._func = func
        self._name = name

    def __eq__(self, other):
        return self._func(other)

    def __repr__(self):
        if self._name is None:
            return "{}({})".format(self.__class__.__name__, self._func.__name__)
        return "{}({})".format(self.__class__.__name__, self._name)
