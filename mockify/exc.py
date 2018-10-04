class Unsatisfied(AssertionError):

    def __init__(self, expectations):
        self._expectations = expectations

    def _format_error(self, expectation):
        return "#{}. {}: {} (expected) != {} (actual)".format(
            expectation._id,
            expectation._mock_call,
            self.__format_expected_calls(expectation._expected_calls),
            self.__format_actual_calls(expectation._actual_calls))

    def __format_call_count(self, count, prefix=""):
        if count == 0:
            return "{}never called".format(prefix)
        elif count == 1:
            return "{}called once".format(prefix)
        elif count == 2:
            return "{}called twice".format(prefix)
        else:
            return "{}called {} times".format(prefix, count)

    def __format_expected_calls(self, count):
        return self.__format_call_count(count, prefix="to be ")

    def __format_actual_calls(self, count):
        return self.__format_call_count(count)

    def __str__(self):
        expectations_gen = (self._format_error(x) for x in self._expectations)
        return "Following expectations were not satisfied:\n\t"\
            "{}".format("\n\t".join(expectations_gen))
