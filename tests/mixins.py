class AssertUnsatisfiedAssertionMatchMixin:

    def assert_unsatisfied_assertion_match(self, excinfo, *matches):
        for i, unsatisfied_expectation in enumerate(excinfo.value.unsatisfied_expectations):
            mock, action, expected, actual = matches[i]
            assert str(unsatisfied_expectation.expected_call) == mock
            assert unsatisfied_expectation.format_action() == action
            assert unsatisfied_expectation.format_expected() == expected
            assert unsatisfied_expectation.format_actual() == actual
