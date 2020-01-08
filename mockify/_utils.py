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

import functools
import itertools


def format_call_count(count):
    if count == 1:
        return "once"
    elif count == 2:
        return "twice"
    else:
        return "{} times".format(count)


def format_args_kwargs(*args, **kwargs):
    args_gen = (repr(x) for x in args)
    kwargs_gen = ("{}={!r}".format(k, v) for k, v in sorted(kwargs.items()))
    all_gen = itertools.chain(args_gen, kwargs_gen)
    return ', '.join(all_gen)


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


class memoized_property:
    """A property that is evaluated once."""

    def __init__(self, fget):
        self.fget = fget

    def __get__(self, obj, objtype):
        if obj is None:
            return self
        else:
            obj.__dict__[self.fget.__name__] = tmp = self.fget(obj)
            return tmp


class ExportList(list):
    """An utility for automated filling in of module's ``__all__``
    property."""

    def __call__(self, obj):
        self.append(obj.__name__)
        return obj


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
