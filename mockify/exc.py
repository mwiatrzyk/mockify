class Unsatisfied(AssertionError):

    def __init__(self, expectations):
        self._expectations = expectations

    def _format_error(self, expectation):
        return "at {}\n\t    Mock: {}\n\tExpected: {}\n\t  Actual: {}".format(
            expectation._fileinfo,
            expectation._mock_call,
            self.__format_expected_calls(expectation),
            self.__format_actual_calls(expectation))

    def __format_expected_calls(self, expectation):
        return str(expectation._expected_calls)

    def __format_actual_calls(self, expectation):
        count = expectation._actual_calls
        if count == 0:
            return "never called"
        elif count == 1:
            return "called once"
        elif count == 2:
            return "called twice"
        else:
            return "called {} times".format(count)

    def __str__(self):
        expectations_gen = (self._format_error(x) for x in self._expectations)
        return "\n".join(expectations_gen)
