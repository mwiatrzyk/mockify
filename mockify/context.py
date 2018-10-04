import itertools

from . import exc


class Context:

    def __init__(self):
        self._expectations = []

    def make_mock(self, name):
        return _Mock(self, name)

    def assert_satisfied(self):
        unsatisfied_expectations = self._find_all_unsatisfied_expectations()
        if unsatisfied_expectations:
            raise exc.Unsatisfied(unsatisfied_expectations)

    def _append_expectation(self, mock_call):
        expectation = _Expectation(len(self._expectations) + 1, mock_call)
        self._expectations.append(expectation)
        return expectation

    def _find_all_unsatisfied_expectations(self):
        return list(filter(lambda x: not x._is_satisfied(), self._expectations))

    def _find_next_expectation_for_mock_call(self, mock_call):
        last = None
        for expectation in self._expectations:
            if expectation._mock_call == mock_call:
                if not expectation._is_satisfied():
                    return expectation
                else:
                    last = expectation
        return last


class _Mock:

    def __init__(self, ctx, name):
        self._ctx = ctx
        self._name = name

    def __call__(self, *args, **kwargs):
        mock_call = _MockCall(self._name, args, kwargs)
        expectation = self._ctx._find_next_expectation_for_mock_call(mock_call)
        if expectation is None:
            raise TypeError("Uninterested mock called: {}".format(mock_call))
        expectation._consume()

    def expect_call(self, *args, **kwargs):
        mock_call = _MockCall(self._name, args, kwargs)
        return self._ctx._append_expectation(mock_call)


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
            self._args == other._args and\
            self._kwargs == other._kwargs


class _Expectation:

    def __init__(self, id_, mock_call):
        self._id = id_
        self._mock_call = mock_call
        self._expected_calls = 1
        self._actual_calls = 0

    def _is_satisfied(self):
        return self._expected_calls == self._actual_calls

    def _consume(self):
        self._actual_calls += 1

    def times(self, cardinality):
        self._expected_calls = cardinality
