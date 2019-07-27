# ---------------------------------------------------------------------------
# mockify/_utils.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------

import traceback


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


def extract_filename_and_lineno_from_stack(offset=0):
    stack = traceback.extract_stack()
    frame = stack[-2 + offset]
    return frame.filename, frame.lineno


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
    """Utility for easier exporting names from module.

    You just need to create an ``__all__`` list::

        __all__ = export = ExportList()

    And then use ``export`` to decorate functions and/or classes you want to
    export::

        @export
        def foo():
            pass
    """

    def __call__(self, cls_or_func):
        self.append(cls_or_func.__name__)
        return cls_or_func
