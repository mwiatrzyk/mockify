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
