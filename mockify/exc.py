class UnsatisfiedExpectationsError(AssertionError):

    def __init__(self, expectations):
        self._expectations = expectations

    def _format_error(self, expectation):
        return "#{}. {}: {} (expected) != {} (actual)".format(
            expectation._id,
            expectation._mock_call,
            self.__format_expected_calls(expectation._expected_calls),
            self.__format_actual_calls(expectation._actual_calls))

    def __format_counter(self, counter):
        if counter == 1:
            return "once"
        elif counter == 2:
            return "twice"
        else:
            return "{} times".format(counter)

    def __format_expected_calls(self, counter):
        if counter == 0:
            return "to be never called"
        else:
            return "to be called {}".format(self.__format_counter(counter))

    def __format_actual_calls(self, counter):
        if counter == 0:
            return "never called"
        else:
            return "called {}".format(self.__format_counter(counter))

    def __str__(self):
        expectations_gen = (self._format_error(x) for x in self._expectations)
        return "Following expectations were not satisfied:\n\t"\
            "{}".format("\n\t".join(expectations_gen))
