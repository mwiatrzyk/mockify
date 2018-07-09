class Mock:

    class _Expectation:

        def __init__(self, func_name):
            self._func_name = func_name
            self._calls = 0
            self._expected_calls = 1

        def __str__(self):
            return "{}(): to be called once (expected), never called (actual)".format(self._func_name)

        def _is_satisfied(self):
            return self._calls == self._expected_calls

        def _consume(self):
            self._calls += 1

    def __init__(self, func_name):
        self._func_name = func_name
        self._expectations = []

    def __call__(self):
        if not self._expectations:
            raise AssertionError("uninterested mock function called: {}()".format(self._func_name))
        self._expectations[0]._consume()

    def expect_call(self):
        self._expectations.append(self._Expectation(self._func_name))

    def assert_satisfied(self):
        unsatisfied_expectations = [x for x in self._expectations if not x._is_satisfied()]
        if unsatisfied_expectations:
            gen = ("{}. {}".format(i+1, str(x)) for i, x in enumerate(unsatisfied_expectations))
            raise AssertionError("mock function has unsatisfied expectations:\n{}".format('\n'.join(gen)))
