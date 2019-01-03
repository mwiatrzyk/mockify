# ---------------------------------------------------------------------------
# mockify/exc.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------


class UninterestedCall(TypeError):
    """Raised when uninterested mock is called.

    Mockify requires each mock call to have matching expectation recorded. If
    none is found during call, then this exception is raised, terminating the
    test.

    :param call:
        Instance of :class:`mockify.engine.Call` class representing uinterested
        mock call
    """

    def __init__(self, call):
        self._call = call

    def __str__(self):
        return str(self.call)

    @property
    def call(self):
        """Instance of :class:`mockify.engine.Call` passed to
        :class:`UninterestedCall` constructor."""
        return self._call


class OversaturatedCall(TypeError):
    """Raised when mock is called more times than expected.

    This exception will be thrown only if mock has actions defined as it does
    not know what to do next if all expected actions were already executed.

    :param expectation:
        Instance of :class:`mockify.engine.Expectation` class representing
        expectation that was oversaturated

    :param call:
        Instance of :class:`mockify.engine.Call` class representing mock call
        that oversaturated ``expectation``
    """

    def __init__(self, expectation, call):
        self._expectation = expectation
        self._call = call

    def __str__(self):
        return "at {}: {}: no more actions recorded for call: {}".format(
            self.expectation.format_location(),
            str(self.expectation.expected_call),
            self.call)

    @property
    def expectation(self):
        """Instance of :class:`mockify.engine.Expectation` passed to
        :class:`OversaturatedCall` constructor."""
        return self._expectation

    @property
    def call(self):
        """Instance of :class:`mockify.engine.Call` passed to
        :class:`OversaturatedCall` constructor."""
        return self._call


class Unsatisfied(AssertionError):
    """Raised by :meth:`mockify.engine.Registry.assert_satisfied` method when
    there is at least one unsatisfied expectation.

    This exception displays explanatory information to the user:

        * file location where unsatisfied expectation was recorded
        * expected call pattern
        * expected call count
        * actual call count
        * next action to be executed (if any)

    :param expectations:
        List of :class:`mockify.engine.Expectation` instances representing all
        unsatisfied expectations
    """

    def __init__(self, expectations):
        self._expectations = expectations

    def __str__(self):
        if len(self.expectations) == 1:
            prefix = 'following expectation is not satisfied:\n\n'
        else:
            prefix = 'following {} expectations are not satisfied:\n\n'.format(len(self.expectations))
        expectations_gen = map(
            lambda x: self.__format_expectation(x), self.expectations)
        return prefix + '\n\n'.join(expectations_gen)

    def __format_expectation(self, expectation):
        rows = ["at {}".format(expectation.format_location())]
        rows.append('-' * len(rows[0]))
        rows.append(
            "{:>13}".format("Pattern: ") + str(expectation.expected_call))
        action = expectation.format_action()
        if action is not None:
            rows.append("{:>13}".format("Action: ") + action)
        rows.extend([
            "{:>13}".format("Expected: ") + expectation.format_expected(),
            "{:>13}".format("Actual: ") + expectation.format_actual()])
        return '\n'.join(rows)

    @property
    def expectations(self):
        """Instance of :class:`mockify.engine.Expectation` passed to
        :class:`Unsatisfied` constructor."""
        return self._expectations
