import traceback
import itertools
import collections

from . import exc, _utils
from .cardinality import Exactly, AtLeast


class Context:

    def __init__(self, ordered=True):
        self._ordered = ordered
        self._expectations = []

    def make_mock(self, name):
        return _Mock(self, name)

    def assert_satisfied(self):
        unsatisfied_expectations = self.__find_all_unsatisfied_expectations()
        if unsatisfied_expectations:
            raise exc.Unsatisfied(unsatisfied_expectations)

    def _register_expectation(self, expectation):
        self._expectations.append(expectation)

    def _find_expectation_for(self, mock_call):
        all_matching = self.__find_all_for(mock_call)
        if not all_matching:
            raise TypeError("Uninterested mock called: {}".format(mock_call))
        if self._ordered:
            return self.__find_ordered(all_matching, mock_call)
        else:
            return self.__find_unordered(all_matching)

    def __find_ordered(self, matching, mock_call):
        next_expected = self.__find_next_expected()
        for expectation in matching:
            if not expectation._is_satisfied() and (next_expected is None or expectation is next_expected):
                return expectation
        if next_expected is not None and matching[-1] is not next_expected:
            raise TypeError("Unexpected mock called: {} (expected) != {} (called)".format(next_expected._mock_call, mock_call))
        return matching[-1]

    def __find_unordered(self, matching):
        for expectation in matching:
            if not expectation._is_satisfied():
                return expectation
        return matching[-1]

    def __find_all_for(self, mock_call):
        return list(filter(lambda x: x._mock_call == mock_call, self._expectations))

    def __find_next_expected(self):
        return next(filter(lambda x: not x._is_satisfied(), self._expectations), None)

    def __find_all_unsatisfied_expectations(self):
        return list(filter(lambda x: not x._is_satisfied(), self._expectations))


class _Mock:

    def __init__(self, ctx, name):
        self._ctx = ctx
        self._name = name

    def __call__(self, *args, **kwargs):
        mock_call = _MockCall(self._name, args, kwargs)
        expectation = self._ctx._find_expectation_for(mock_call)
        return expectation._consume(*args, **kwargs)

    def expect_call(self, *args, **kwargs):
        stack = traceback.extract_stack()
        frame_summary = stack[-2]
        mock_call = _MockCall(self._name, args, kwargs)
        expectation = _Expectation(frame_summary, mock_call)
        self._ctx._register_expectation(expectation)
        return expectation


class _MockCall:

    def __init__(self, name, args, kwargs):
        self._name = name
        self._args = args
        self._kwargs = kwargs

    def __str__(self):
        args_gen = (str(x) for x in self._args)
        kwargs_gen = ("{}={!r}".format(k, v) for k, v in sorted(self._kwargs.items()))
        all_gen = itertools.chain(args_gen, kwargs_gen)
        return "{}({})".format(self._name, ", ".join(all_gen))

    def __eq__(self, other):
        return self._name == other._name and\
            len(self._args) == len(other._args) and\
            self._args == other._args and\
            self._kwargs == other._kwargs


class _Expectation:

    def __init__(self, frame_summary, mock_call):
        self._frame_summary = frame_summary
        self._mock_call = mock_call
        self._actual_calls = 0
        self._actions = collections.deque()
        self._repeated_action = None
        self.__expected_calls = None

    @property
    def _expected_calls(self):
        return self.__expected_calls or Exactly(1)

    @_expected_calls.setter
    def _expected_calls(self, value):
        self.__expected_calls = value

    @property
    def _fileinfo(self):
        return "{}:{}".format(self._frame_summary.filename, self._frame_summary.lineno)

    def _is_satisfied(self):
        return self._expected_calls._satisfies_actual(self._actual_calls)

    def _consume(self, *args, **kwargs):
        self._actual_calls += 1
        if self._actions:
            return self._actions.popleft()(*args, **kwargs)
        elif self._repeated_action is not None:
            return self._repeated_action(*args, **kwargs)

    def times(self, cardinality):
        if not _utils.is_cardinality_object(cardinality):
            cardinality = Exactly(cardinality)
        self._expected_calls = cardinality
        return self

    def will_once(self, action):
        self._actions.append(action)
        self._expected_calls = Exactly(len(self._actions))
        return self

    def will_repeatedly(self, action):
        self._repeated_action = action
        if self._actions:
            self._expected_calls = AtLeast(len(self._actions))
        elif self.__expected_calls is None:
            self._expected_calls = AtLeast(0)
        return self
