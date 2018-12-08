# ---------------------------------------------------------------------------
# mockify/cardinality.py
#
# Copyright (C) 2018 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------

from mockify import _utils


class Exactly:

    def __init__(self, expected):
        if expected < 0:
            raise TypeError("value of 'expected' must be >= 0")
        self._expected = expected

    def __eq__(self, actual):
        return self._expected == actual

    def format_expected(self):
        if self._expected == 0:
            return "to be never called"
        else:
            return "to be called {}".format(_utils.format_call_count(self._expected))


class AtLeast:

    def __init__(self, minimal):
        if minimal < 0:
            raise TypeError("value of 'minimal' must be >= 0")
        self._minimal = minimal

    def __eq__(self, actual):
        return actual >= self._minimal

    def format_expected(self):
        return "to be called at least {}".format(format_call_count(self._minimal))


class AtMost:

    def __new__(cls, maximal):
        if maximal < 0:
            raise TypeError("value of 'maximal' must be >= 0")
        elif maximal == 0:
            return Exactly(maximal)
        else:
            return super().__new__(cls)

    def __init__(self, maximal):
        super().__init__()
        self._maximal = maximal

    def format_expected(self):
        return "to be called at most {}".format(format_call_count(self._maximal))

    def is_satisfied(self):
        return self._maximal >= self._actual


class Between:

    def __new__(cls, minimal, maximal):
        if minimal > maximal:
            raise TypeError("value of 'minimal' must not be greater than 'maximal'")
        elif minimal < 0:
            raise TypeError("value of 'minimal' must be >= 0")
        elif minimal == maximal:
            return Exactly(maximal)
        elif minimal == 0:
            return AtMost(maximal)
        else:
            return super().__new__(cls)

    def __init__(self, minimal, maximal):
        super().__init__()
        self._minimal = minimal
        self._maximal = maximal

    def format_expected(self):
        return "to be called at least {} but no more than {}".\
            format(format_call_count(self._minimal), format_call_count(self._maximal))

    def is_satisfied(self):
        return self._minimal <= self._actual <= self._maximal
