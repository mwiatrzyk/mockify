# ---------------------------------------------------------------------------
# mockify/exc.py
#
# Copyright (C) 2018 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------


class UninterestedCall(TypeError):
    """Raised when mock is called but there were no matching expectations
    found.

    :param call:
        Instance of :class:`mockify.engine.Call` class representing mock call
    """

    def __init__(self, call):
        self._call = call

    def __str__(self):
        return str(self.call)

    @property
    def call(self):
        return self._call


class OversaturatedCall(TypeError):
    """Raised when mock is called more times than expected.

    This exception will be thrown only if mock has actions defined as it does
    not know what to do next if all expected actions were already executed.

    :param call:
        Instance of :class:`mockify.engine.Call` class representing mock call
    """

    def __init__(self, call):
        self._call = call

    def __str__(self):
        return str(self.call)

    @property
    def call(self):
        return self._call


class Unsatisfied(AssertionError):

    def __init__(self, unsatisfied_expectations):
        self._unsatisfied_expectations = unsatisfied_expectations

    def __str__(self):
        expectations_gen = map(
            lambda x: self.__format_expectation(x), self.unsatisfied_expectations)
        return 'following {} expectation(-s) are not satisfied:\n\n'.\
            format(len(self.unsatisfied_expectations)) + '\n\n'.join(expectations_gen)

    def __format_expectation(self, expectation):
        rows = ["at {}".format(expectation.format_location())]
        rows.append('-' * len(rows[0]))
        rows.extend([
            "{:>13}".format("Pattern: ") + str(expectation.expected_call),
            "{:>13}".format("Expected: ") + expectation.format_expected(),
            "{:>13}".format("Actual: ") + expectation.format_actual()])
        return '\n'.join(rows)

    @property
    def unsatisfied_expectations(self):
        return self._unsatisfied_expectations


class Satisfied(AssertionError):

    def __init__(self, registry):
        self._registry = registry

    def __str__(self):
        return "some expectations registered in {!r} are unexpectedly satisfied".format(self.registry)

    @property
    def registry(self):
        return self._registry
