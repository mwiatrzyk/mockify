class Unsatisfied(AssertionError):

    def __init__(self, expectations):
        self._expectations = expectations

    @property
    def expectations(self):
        return self._expectations

    def _format_error(self, expectation):
        return "at {}:{}\n\t    Mock: {}\n\tExpected: {}\n\t  Actual: {}".format(
            expectation.filename, expectation.lineno,
            expectation.mock_call,
            expectation.call_count.format_expected(),
            expectation.call_count.format_actual())

    def __str__(self):
        expectations_gen = (self._format_error(x) for x in self._expectations)
        return "\n".join(expectations_gen)
