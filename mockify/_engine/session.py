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


class Config:

    def __init__(self):
        self._config = {
            'uninterested_call_strategy': 'fail'
        }

    def get(self, key):
        return self._config.get(key)

    def set(self, key, value):
        validate = getattr(self, f"_validate_{key}", None)
        if validate is not None:
            validate(key, value)
        self._config[key] = value

    def _validate_uninterested_call_strategy(self, key, value):
        if value not in ('fail', 'warn', 'ignore'):
            raise ValueError(f"Invalid value for {key!r} config option given: {value!r}")


class Session:
    """Used to create repositories for :class:`mockify.Expectation`
    instances."""

    def __init__(self):
        self._unordered_expectations = []
        self._ordered_expectations = collections.deque()
        self._ordered_expectations_enabled_for = set()
        self._config = Config()

    @property
    def config(self):
        """Set or get configuration options for this session.

        This property returns a configuration object providing following
        methods:

        * **get(key)** for getting option matching *key*,
        * and **set(key, value)** for setting option *key* to given *value*.
        """
        return self._config

    def __call__(self, actual_call):
        """Trigger expectation matching *actual_call* received from mock
        being called.

        This method compares given *actual_call* with
        :attr:`mockify.Expectation.expected_call` attribute of each
        expectation to find a one that matches the call.
        """
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
            return found_by_call[-1](actual_call)  # Oversaturate last found if all are satisfied

    def __handle_uninterested_call(self, actual_call):
        uninterested_call_strategy = self._config.get('uninterested_call_strategy')
        if uninterested_call_strategy == 'fail':
            self.__handle_uninterested_call_using_fail_strategy(actual_call)
        elif uninterested_call_strategy == 'ignore':
            pass
        elif uninterested_call_strategy == 'warn':
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
