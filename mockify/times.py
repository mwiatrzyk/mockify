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


class TimesBase:

    def __ne__(self, other):
        return not self.__eq__(other)


class Exactly(TimesBase):

    def __init__(self, expected):
        if expected < 0:
            raise TypeError("value of 'expected' must be >= 0")
        self._expected = expected

    def __eq__(self, actual):
        return self._expected == actual

    def __add__(self, minimal):
        return self.__class__(self._expected + minimal)

    def format_expected(self):
        return _utils.format_expected_call_count(self._expected)


class AtLeast(TimesBase):

    def __init__(self, minimal):
        if minimal < 0:
            raise TypeError("value of 'minimal' must be >= 0")
        self._minimal = minimal

    def __eq__(self, actual):
        return actual >= self._minimal

    def __add__(self, minimal):
        return self.__class__(self._minimal + minimal)

    def format_expected(self):
        if self._minimal == 0:
            return "to be called optionally"
        else:
            return "to be called at least {}".format(_utils.format_call_count(self._minimal))


class AtMost(TimesBase):

    def __new__(cls, maximal):
        if maximal < 0:
            raise TypeError("value of 'maximal' must be >= 0")
        elif maximal == 0:
            return Exactly(maximal)
        else:
            return super().__new__(cls)

    def __init__(self, maximal):
        self._maximal = maximal

    def __eq__(self, actual):
        return actual <= self._maximal

    def __add__(self, minimal):
        return Between(minimal, self._maximal + minimal)

    def format_expected(self):
        return "to be called at most {}".format(_utils.format_call_count(self._maximal))


class Between(TimesBase):

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
        self._minimal = minimal
        self._maximal = maximal

    def __eq__(self, actual):
        return actual >= self._minimal and\
            actual <= self._maximal

    def __add__(self, minimal):
        return self.__class__(self._minimal + minimal, self._maximal + minimal)

    def format_expected(self):
        return "to be called between {} and {} times".format(self._minimal, self._maximal)
