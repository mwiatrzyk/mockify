class UninterestedMockCall(TypeError):

    def __init__(self, mock_call):
        self._mock_call = mock_call

    def __str__(self):
        return "Uninterested mock call: {}".format(self._mock_call)


class UnexpectedMockCall(TypeError):

    def __init__(self, expectation, actual_mock_call):
        self._expectation = expectation
        self._actual_mock_call = actual_mock_call

    def __str__(self):
        return "Unexpected mock called:\n\tExpected: {} (at {}:{})\n\t  Actual: {}".\
            format(self._expectation.mock_call, self._expectation.filename, self._expectation.lineno,
                self._actual_mock_call)


class Unsatisfied(AssertionError):

    def __init__(self, expectations):
        self._unsatisfied_expectations = list(x for x in expectations if not x.is_satisfied())
        self._total_count = len(expectations)

    @property
    def expectations(self):
        return self._unsatisfied_expectations

    def _format_error(self, expectation):
        return "at {}:{}\n\t    Mock: {}\n\tExpected: {}\n\t  Actual: {}".format(
            expectation.filename, expectation.lineno,
            expectation.mock_call,
            expectation.call_count.format_expected(),
            expectation.call_count.format_actual())

    def __str__(self):
        expectations_gen = (self._format_error(x) for x in self._unsatisfied_expectations)
        return "{} out of total {} expectations are not satisfied:\n".format(len(self._unsatisfied_expectations), self._total_count)\
            + "\n".join(expectations_gen)
