# ---------------------------------------------------------------------------
# mockify/_utils.py
#
# Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring

import functools
import itertools
import keyword
import weakref


def format_call_count(count):
    if count == 1:
        return "once"
    if count == 2:
        return "twice"
    return "{} times".format(count)


def validate_mock_name(name):
    """Check if *name* can be used as a mock name."""
    parts = name.split('.') if isinstance(name, str) else [name]
    for part in parts:
        if not is_identifier(part):
            raise TypeError(
                "Mock name must be a valid Python identifier, got {!r} instead".
                format(name)
            )


def is_identifier(name):
    """Check if given name is a valid Python identifier."""
    return isinstance(name, str) and\
        name.isidentifier() and\
        not keyword.iskeyword(name)


def log_unhandled_exceptions(logger):
    """A decorator that logs unhandled exceptions using provided logger.

    This is meant to be used to decorate special methods like __str__ that
    cannot throw exceptions. It allows easier debugging during library
    development.
    """

    def decorator(func):

        @functools.wraps(func)
        def proxy(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                logger.error(
                    'An unhandled exception occurred during {func!r} call:',
                    exc_info=True
                )
                raise

        return proxy

    return decorator


def make_weak(value):
    if value is not None:
        return weakref.ref(value)
    return value


class ArgsKwargsFormatter:
    """A helper to return string representation of given args and kwargs.

    :param formatter:
        Formatter to be used to render string representation of function's
        arguments

    :param sort:
        Choose if keyword args (if any) should be alphabetically sorted or
        not

    :param skip_kwarg_if:
        A function to be used to test each keyword argument.

        If the function evaluates to true, that keyword argument will be
        removed from string representation.
    """

    def __init__(self, formatter=repr, sort=True, skip_kwarg_if=None):
        self._formatter = formatter
        self._sort = sort
        self._skip_kwarg_if = skip_kwarg_if

    def format(self, *args, **kwargs):
        """Render string representation of given args and kwargs."""
        args_gen = map(self._formatter, args)
        kwargs_gen = sorted(kwargs.items()) if self._sort else kwargs.items()
        if self._skip_kwarg_if is not None:
            kwargs_gen = filter(
                lambda x: not self._skip_kwarg_if(x[1]), kwargs_gen
            )
        kwargs_gen = map(
            lambda x: "{}={}".format(x[0], self._formatter(x[1])), kwargs_gen
        )
        all_gen = itertools.chain(args_gen, kwargs_gen)
        return ', '.join(all_gen)


class ErrorMessageBuilder:
    """A helper class for easier building of assertion messages."""

    def __init__(self):
        self._lines = []

    def build(self):
        return '\n'.join(self._lines)

    def append_line(self, template, *args, **kwargs):
        self._lines.append(template.format(*args, **kwargs))

    def append_location(self, location):
        self._lines.extend(
            ["at {}".format(location), "-" * (len(str(location)) + 3)]
        )


class IterableQuery:
    """A helper class for querying iterables."""

    def __init__(self, iterable):
        self._iterable = iterable

    def find_first(self, func):
        """Find and return first item matching given *func*.

        If no matching item was found, then return ``None``.
        """
        return next(filter(func, self._iterable), None)

    def exists(self, func):
        """Check if there is an item matching *func*."""
        return self.find_first(func) is not None


class DictEqualityMixin:
    """A helper class that adds ``__eq__`` and ``__ne__`` operators that
    compare ``__dict__`` attributes of two objects.

    If both objects are instances of same class and both have ``__dict__``
    shallow equal, then these two objects are considered **equal**.
    """

    def __eq__(self, other):
        return type(self) is type(other) and\
            self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)
