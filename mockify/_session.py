import warnings
import collections

from . import exc
from ._expectation import Expectation


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
        found_by_call = list(self.expectations.by_call(actual_call))
        if not found_by_call:
            return self.__handle_uninterested_call(actual_call)
        for expectation in found_by_call:
            if not expectation.is_satisfied():
                return expectation(actual_call)
        else:
            return found_by_call[-1](actual_call)  # Oversaturate last found if all are satisfied

    def __handle_uninterested_call(self, actual_call):
        if self.uninterested_call_strategy == 'fail':
            self.__handle_uninterested_call_using_fail_strategy(actual_call)
        elif self.uninterested_call_strategy == 'ignore':
            pass
        elif self.uninterested_call_strategy == 'warn':
            warnings.warn(str(actual_call), exc.UninterestedCallWarning)

    def __handle_uninterested_call_using_fail_strategy(self, actual_call):
        found_by_name = list(self.expectations.by_name(actual_call.name))
        if not found_by_name:
            raise exc.UninterestedCall(actual_call)
        else:
            raise exc.UnexpectedCall(actual_call, found_by_name)

    @property
    def expectations(self):
        return ExpectationFilter(self._unordered_expectations)

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
        unsatisfied_expectations = list(self.expectations.unsatisfied())
        if unsatisfied_expectations:
            raise exc.Unsatisfied(unsatisfied_expectations)

    def enable_ordered(self, *names):
        unordered_expectations = list(self._unordered_expectations)
        self._unordered_expectations = []
        self._ordered_expectations = collections.deque()
        self._ordered_expectations_enabled_for = set(names)
        for expectation in unordered_expectations:
            if self._is_ordered(expectation.expected_call):
                self._ordered_expectations.append(expectation)
            else:
                self._unordered_expectations.append(expectation)

    def disable_ordered(self):
        if self._ordered_expectations:  # TODO: move this back to unordered list
            raise AssertionError("FIXME: non-consumed ordered expectations still present")
        self._ordered_expectations_enabled_for = set()

    def _is_ordered(self, call):
        for prefix in self._ordered_expectations_enabled_for:
            if call.name.startswith(prefix):
                return True
        return False


class ExpectationFilter:

    def __init__(self, expectations):
        self._expectations = expectations

    def __iter__(self):
        return iter(self._expectations)

    def by_func(self, func):
        return self.__class__(
            filter(func, self._expectations))

    def by_call(self, call):
        return self.by_func(lambda x: x.expected_call == call)

    def by_name(self, name):
        return self.by_func(lambda x: x.expected_call.name == name)

    def by_name_prefix(self, prefix):
        return self.by_func(lambda x: x.expected_call.name.startswith(prefix))

    def unsatisfied(self):
        return self.by_func(lambda x: not x.is_satisfied())

    def count(self):
        self._expectations = list(self._expectations)
        return len(self._expectations)
