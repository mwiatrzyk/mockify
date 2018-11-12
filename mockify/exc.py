class UninterestedCall(TypeError):

    def __init__(self, call):
        self._call = call

    @property
    def call(self):
        return self._call

    def __str__(self):
        return "at {}:{}: {}".format(self._call.filename, self._call.lineno, self._call)


class UnsatisfiedAssertion(AssertionError):

    def __init__(self, unsatisfied_expectations):
        self._unsatisfied_expectations = unsatisfied_expectations

    @property
    def unsatisfied_expectations(self):
        return self._unsatisfied_expectations

    def _format_error(self, index, expectation):
        expected_call = expectation.expected_call
        formatted_action = expectation.format_action()
        heading = "#{} at {}:{}".format(index, expected_call.filename, expected_call.lineno)
        return "{}\n"\
            "{}\n"\
            "      Mock: {}\n"\
            "{}"\
            "  Expected: {}\n"\
            "    Actual: {}".format(
                heading, '-' * len(heading),
                expected_call,
                "    Action: {}\n".format(formatted_action) if formatted_action else '',
                expectation.format_expected(),
                expectation.format_actual())

    def __str__(self):
        expectations_gen = (self._format_error(i+1, x) for i, x in enumerate(self._unsatisfied_expectations))
        return 'Following expectations have failed:\n\n' + '\n\n'.join(expectations_gen)
