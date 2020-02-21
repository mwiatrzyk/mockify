# ---------------------------------------------------------------------------
# mockify/_utils.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import keyword
import functools
import itertools


def format_call_count(count):
    if count == 1:
        return "once"
    elif count == 2:
        return "twice"
    else:
        return "{} times".format(count)


def format_args_kwargs(args, kwargs, formatter=repr, sort=True, skip_kwarg_if=None):
    args_gen = map(formatter, args)
    kwargs_gen = sorted(kwargs.items()) if sort else kwargs.items()
    if skip_kwarg_if is not None:
        kwargs_gen = filter(lambda x: not skip_kwarg_if(x[1]), kwargs_gen)
    kwargs_gen = map(lambda x: "{}={}".format(x[0], formatter(x[1])), kwargs_gen)
    all_gen = itertools.chain(args_gen, kwargs_gen)
    return ', '.join(all_gen)


def validate_mock_name(name):
    """Check if *name* can be used as a mock name."""
    parts = name.split('.') if isinstance(name, str) else [name]
    for part in parts:
        if not is_identifier(part):
            raise TypeError(f"Mock name must be a valid Python identifier, got {name!r} instead")


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
                logger.error('An unhandled exception occurred during {func!r} call:', exc_info=True)
                raise

        return proxy

    return decorator


class ErrorMessageBuilder:
    """A helper class for easier building of assertion messages."""

    def __init__(self):
        self._lines = []

    def build(self):
        return '\n'.join(self._lines)

    def append_line(self, template, *args, **kwargs):
        self._lines.append(template.format(*args, **kwargs))

    def append_location(self, location):
        self._lines.extend([
            f"at {location}",
            "-" * (len(str(location)) + 3)
        ])


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
