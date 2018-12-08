# ---------------------------------------------------------------------------
# mockify/_utils.py
#
# Copyright (C) 2018 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------

_next_id = 0


def is_cardinality_object(obj):
    return hasattr(obj, "_actual")


def format_call_count(count):
    if count == 1:
        return "once"
    elif count == 2:
        return "twice"
    else:
        return "{} times".format(count)


def next_unique_id():
    global _next_id
    _next_id += 1
    return _next_id
