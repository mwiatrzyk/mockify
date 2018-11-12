import traceback

from mockify import exc, Call, Expectation


class FunctionMock:

    def __init__(self, name):
        self._name = name
        self._expectations = []

    def __call__(self, *args, **kwargs):
        filename, lineno = self._extract_owning_method_call_location()
        call = Call(self._name, filename, lineno).bind(*args, **kwargs)
        matching_expectations = list(filter(lambda x: x.expected_call == call, self._expectations))
        if not matching_expectations:
            raise exc.UninterestedCall(call)
        for expectation in matching_expectations:
            if not expectation.is_satisfied():
                return expectation(call)
        else:
            return matching_expectations[-1](call)

    def expect_call(self, *args, **kwargs):
        filename, lineno = self._extract_owning_method_call_location()
        call = Call(self._name, filename, lineno).bind(*args, **kwargs)
        expectation = Expectation(call)
        self._expectations.append(expectation)
        return expectation

    def assert_satisfied(self):
        unsatisfied_expectations = list(filter(lambda x: not x.is_satisfied(), self._expectations))
        if unsatisfied_expectations:
            raise exc.UnsatisfiedAssertion(unsatisfied_expectations)

    def assert_not_satisfied(self):
        try:
            self.assert_satisfied()
            raise AssertionError("function mock {!r} is expected not to be satisfied, but it is".format(self._name))
        except exc.UnsatisfiedAssertion:
            pass

    def _extract_owning_method_call_location(self):
        stack = traceback.extract_stack()
        frame_summary = stack[-3]
        return frame_summary.filename, frame_summary.lineno
