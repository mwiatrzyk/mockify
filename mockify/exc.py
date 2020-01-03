# ---------------------------------------------------------------------------
# mockify/exc.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import logging

logger = logging.getLogger('mockify')


class MockifyWarning(Warning):
    """Common base class for Mockify warnings.

    .. versionadded:: 1.0
    """


class UninterestedCallWarning(MockifyWarning):
    """This warning is used to inform about uninterested call being made.

    It is only used when uninterested call strategy is changed in mocking
    session. See :class:`mockify.Session` for more details.

    .. versionadded:: 1.0
    """


class MockifyError(Exception):
    """Common base class for all Mockify exceptions.

    .. versionadded:: 1.0
    """

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class InvalidMockName(MockifyError):
    """Raised when you choose incorrect name for your mock.

    Mock names are simply string objects, but (for various reasons) that
    names are restricted to be valid Python identifiers (which are f.e.
    variable names).

    .. versionadded:: 1.0
    """

    def __str__(self):
        return f"Mock name must be a valid Python identifier, got {self.invalid_name!r} instead"


class MockifyAssertion(MockifyError, AssertionError):
    """Common base class for all Mockify assertion errors.

    With this exception it will be easy to re-raise Mockify-specific
    assertion exceptions for example during debugging.

    .. versionadded:: 1.0
    """


class UnexpectedCall(MockifyAssertion):
    """Informs that mock was called with parameters that couldn't be matched
    to any of expected ones.

    This exception was added to differentiate such mock calls (which can be
    pretty frequent) from the ones that does not have any expectations
    defined (that are still handled by :exc:`mockify.exc.UninterestedCall`
    exception).

    .. versionadded:: 1.0
    """

    def __init__(self, actual_call, candidate_expectations):
        self._actual_call = actual_call
        self._candidate_expectations = candidate_expectations

    def __str__(self):
        try:
            return self.__prepare_str()
        except Exception:
            logger.error('An exception was raised during __str__() evaluation:', exc_info=True)

    def __prepare_str(self):
        location = self._actual_call.location.format_message()
        message = ["No matching expectations found:\n",
            f"at {location}",
            "-" * (len(location) + 3),
            f"Actual:",
            f"  {self._actual_call}",
            f"Candidates:",
        ]
        for i, expectation in enumerate(self._candidate_expectations):
            message.append(f"  {i+1}) {expectation.expected_call}")
        return '\n'.join(message)

    @property
    def actual_call(self):
        return self._actual_call

    @property
    def candidate_expectations(self):
        return self._candidate_expectations


class UnexpectedCallOrder(MockifyAssertion):
    """Raised when mock was called in unexpected order.

    This can only be raised if you use ordered expectations (see
    :func:`mockify.ordered` for more details), but code you are testing calls
    a mock in invalid order.

    .. versionadded:: 1.0
    """

    def __init__(self, actual_call, expected_call):
        self.actual_call = actual_call
        self.expected_call = expected_call

    def __str__(self):
        location = "{}:{}".format(*self.actual_call.location)
        message = ['Another mock was expected to be called:\n',
            f"at {location}",
            f'-' * (len(location) + 3),
            f"Actual:",
            f"  {self.actual_call}",
            f"Expected:",
            f"  {self.expected_call}"
        ]
        return '\n'.join(message)


class UninterestedCall(MockifyAssertion):
    """Raised when uninterested mock is called.

    This exception is raised when you call a mock that does not have any
    expectations defined. It can be intercepted by changing unexpected call
    strategy (see :class:`mockify.Session` for more details).

    :param actual_call:
        Instance of :class:`mockify.Call` object representing uninterested
        call being made
    """

    def __init__(self, actual_call):
        self._actual_call = actual_call

    def __str__(self):
        location = "{}:{}".format(*self.actual_call.location)
        message = [
            "No expectations recorded for mock:\n",
            f"at {location}",
            "-" * (len(location) + 3),
            "Actual:",
            f"  {self.call}"
        ]
        return '\n'.join(message)

    @property
    def actual_call(self):
        """Instance of :class:`mockify.engine.Call` passed to
        :class:`UninterestedCall` constructor."""
        return self._actual_call


class OversaturatedCall(MockifyAssertion):
    """Raised when mock is executed but there are no more actions to be
    performed.

    It is assumed that once mock has at least one action explicitly defined
    by test writer (f.e. using :meth:`mockify.Expectation.will_once` method)
    it cannot work with a default action (i.e. returning ``None``).

    :param oversaturated_expectation:
        Instance of :class:`mockify.Expectation` class representing
        expectation that was oversaturated.

    :param actual_call:
        Instance of :class:`mockify.Call` class containing actual mock call
        parameters
    """

    def __init__(self, oversaturated_expectation, actual_call):
        self._oversaturated_expectation = oversaturated_expectation
        self._actual_call = actual_call

    def __str__(self):
        return "at {}: {}: no more actions recorded for call: {}".format(
            self.expectation.format_location(),
            str(self.expectation.expected_call),
            self.call)

    @property
    def oversaturated_expectation(self):
        return self._oversaturated_expectation

    @property
    def actual_call(self):
        return self._actual_call


class Unsatisfied(MockifyAssertion):
    """Raised by :func:`mockify.satisfied` or :meth:`mockify.Session.done`
    during check if all mocks are satisfied.

    A mock can only be satisfied if all expectations that were declared for
    it are consumed according to expectation specification. This exception is
    never raised during mock calls.

    :param unsatisfied_expectations:
        List of :class:`mockify.Expectation` instances representing
        unsatisfied expectations
    """

    def __init__(self, unsatisfied_expectations):
        self._unsatisfied_expectations = unsatisfied_expectations

    def __str__(self):
        try:
            return self.__prepare_str()
        except Exception:
            logger.error('An exception was raised during __str__() evaluation:', exc_info=True)

    def __prepare_str(self):
        if len(self.unsatisfied_expectations) == 1:
            prefix = 'following expectation is not satisfied:\n\n'
        else:
            prefix = 'following {} expectations are not satisfied:\n\n'.format(len(self.unsatisfied_expectations))
        expectations_gen = map(
            lambda x: self.__format_expectation(x), self.unsatisfied_expectations)
        return prefix + '\n\n'.join(expectations_gen)

    def __format_expectation(self, expectation):
        rows = ["at {}".format(expectation.expected_call.location.format_message())]
        rows.append('-' * len(rows[0]))
        rows.append(
            "{:>13}".format("Pattern: ") + str(expectation.expected_call))
        action = expectation.next_action.format_message() if expectation.next_action is not None else None
        if action is not None:
            rows.append("{:>13}".format("Action: ") + action)
        rows.extend([
            "{:>13}".format("Expected: ") + expectation.expected_call_count.format_message(),
            "{:>13}".format("Actual: ") + expectation.actual_call_count.format_message()])
        return '\n'.join(rows)

    @property
    def unsatisfied_expectations(self):
        """List of all unsatisfied expectation objects.

        .. versionchanged:: 1.0
            Previous ``expectations`` property was renamed.
        """
        return self._unsatisfied_expectations
