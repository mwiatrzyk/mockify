# ---------------------------------------------------------------------------
# mockify/_utils.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import itertools


def format_call_count(count):
    if count == 1:
        return "once"
    elif count == 2:
        return "twice"
    else:
        return "{} times".format(count)


def format_actual_call_count(count):
    if count == 0:
        return 'never called'
    else:
        return 'called ' + format_call_count(count)


def format_expected_call_count(count):
    if count == 0:
        return 'to be never called'
    else:
        return 'to be called ' + format_call_count(count)


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
