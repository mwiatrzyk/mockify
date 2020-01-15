# ---------------------------------------------------------------------------
# mockify/_engine/session.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import warnings
import itertools
import collections

from .. import exc
from .expectation import Expectation


class Session:
    _uninterested_call_strategies = ('fail', 'warn', 'ignore')

    def __init__(self, uninterested_call_strategy='fail'):
        self._unordered_expectations = []
        self._ordered_expectations = collections.deque()
        self._ordered_expectations_enabled_for = set()
        self.uninterested_call_strategy = uninterested_call_strategy

    def __call__(self, actual_call):
        if self._is_ordered(actual_call):
            return self.__call_ordered(actual_call)
        else:
            return self.__call_unordered(actual_call)

    def __call_ordered(self, actual_call):
        head = self._ordered_expectations[0]
        if head.expected_call == actual_call:
            try:
                return head(actual_call)
            finally:
                if head.is_satisfied():
                    self._ordered_expectations.popleft()
        else:
            raise exc.UnexpectedCallOrder(actual_call, head.expected_call)

    def __call_unordered(self, actual_call):
        found_by_call = [x for x in self.expectations if x.expected_call == actual_call]
        if not found_by_call:
            return self.__handle_uninterested_call(actual_call)
        for expectation in found_by_call:
            if not expectation.is_satisfied():
                return expectation(actual_call)
        else:
            print(found_by_call)
            return found_by_call[-1](actual_call)  # Oversaturate last found if all are satisfied

    def __handle_uninterested_call(self, actual_call):
        if self.uninterested_call_strategy == 'fail':
            self.__handle_uninterested_call_using_fail_strategy(actual_call)
        elif self.uninterested_call_strategy == 'ignore':
            pass
        elif self.uninterested_call_strategy == 'warn':
            warnings.warn(str(actual_call), exc.UninterestedCallWarning)

    def __handle_uninterested_call_using_fail_strategy(self, actual_call):
        found_by_name = [x.expected_call for x in self.expectations if x.expected_call.name == actual_call.name]
        if not found_by_name:
            raise exc.UninterestedCall(actual_call)
        else:
            raise exc.UnexpectedCall(actual_call, found_by_name)

    @property
    def expectations(self):
        return itertools.chain(
            self._unordered_expectations,
            self._ordered_expectations)

    @property
    def uninterested_call_strategy(self):
        return self._uninterested_call_strategy

    @uninterested_call_strategy.setter
    def uninterested_call_strategy(self, value):
        if value not in self._uninterested_call_strategies:
            raise ValueError(f"invalid strategy given: {value}")
        self._uninterested_call_strategy = value

    def expect_call(self, expected_call):
        expectation = Expectation(expected_call)
        self._unordered_expectations.append(expectation)
        return expectation

    def done(self):
        unsatisfied_expectations = [x for x in self.expectations if not x.is_satisfied()]
        if unsatisfied_expectations:
            raise exc.Unsatisfied(unsatisfied_expectations)

    def enable_ordered(self, names):
        self._ordered_expectations_enabled_for = set(names)
        unordered_expectations = list(self._unordered_expectations)
        self._unordered_expectations = []
        self._ordered_expectations = collections.deque()
        for expectation in unordered_expectations:
            if self._is_ordered(expectation.expected_call):
                self._ordered_expectations.append(expectation)
            else:
                self._unordered_expectations.append(expectation)

    def disable_ordered(self):
        if self._ordered_expectations:
            self._unordered_expectations.extend(self._ordered_expectations)
        self._ordered_expectations = []
        self._ordered_expectations_enabled_for = set()

    def _is_ordered(self, call):
        return call.name in self._ordered_expectations_enabled_for
