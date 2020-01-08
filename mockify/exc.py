# ---------------------------------------------------------------------------
# mockify/exc.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import logging

from . import _utils

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


class MockifyAssertion(MockifyError, AssertionError):
    """Common base class for all Mockify assertion errors.

    With this exception it will be easy to re-raise Mockify-specific
    assertion exceptions for example during debugging.

    .. versionadded:: 1.0
    """


class UnexpectedCall(MockifyAssertion):
    """Raised when mock was called with parameters that couldn't been matched
    to any of existing expectations.

    This exception was added for easier debugging of failing tests; unlike
    :exc:`UninterestedCall` exception, this one signals that there are
    expectations set for mock that was called.

    .. versionadded:: 1.0

    :param actual_call:
        Instance of :class:`mockify.Call` representing parameters of call
        that was made

    :param expected_calls:
        List of :class:`mockify.Call` instances, each representing expected
        parameters of single expectation
    """

    def __init__(self, actual_call, expected_calls):
        self._actual_call = actual_call
        self._expected_calls = expected_calls

    @_utils.log_unhandled_exceptions(logger)
    def __str__(self):
        builder = _utils.ErrorMessageBuilder()
        builder.append_line('No matching expectations found for call:')
        builder.append_line('')
        builder.append_location(self._actual_call.location)
        builder.append_line('Called:')
        builder.append_line('  {}', self._actual_call)
        builder.append_line('Expected (any of):')
        for i, call in enumerate(self._expected_calls):
            builder.append_line('  {}', call)
        return builder.build()

    @property
    def actual_call(self):
        return self._actual_call

    @property
    def expected_calls(self):
        return self._expected_calls


class UnexpectedCallOrder(MockifyAssertion):
    """Raised when mock was called but another one is expected to be called
    before.

    This can only be raised if you use ordered expectations. See
    :func:`mockify.ordered` for more details.

    .. versionadded:: 1.0

    :param actual_call:
        The call that was made

    :param expected_call:
        The call that is expected to be made
    """

    def __init__(self, actual_call, expected_call):
        self._actual_call = actual_call
        self._expected_call = expected_call

    @_utils.log_unhandled_exceptions(logger)
    def __str__(self):
        builder = _utils.ErrorMessageBuilder()
        builder.append_line('Another mock is expected to be called:')
        builder.append_line('')
        builder.append_location(self._actual_call.location)
        builder.append_line('Called:')
        builder.append_line('  {}', self._actual_call)
        builder.append_line('Expected:')
        builder.append_line('  {}', self._expected_call)
        return builder.build()

    @property
    def actual_call(self):
        return self._actual_call

    @property
    def expected_call(self):
        return self._expected_call


class UninterestedCall(MockifyAssertion):
    """Raised when call is made to a mock that has no expectations set.

    This exception can be disabled by changing unexpected call strategy. See
    :class:`mockify.Session` for more details.

    :param actual_call:
        The call that was made
    """

    def __init__(self, actual_call):
        self._actual_call = actual_call

    @_utils.log_unhandled_exceptions(logger)
    def __str__(self):
        builder = _utils.ErrorMessageBuilder()
        builder.append_line('No expectations recorded for mock:')
        builder.append_line('')
        builder.append_location(self._actual_call.location)
        builder.append_line('Called:')
        builder.append_line('  {}', self._actual_call)
        builder.append_line('Expected:')
        builder.append_line('  no expectations recorded')
        return builder.build()

    @property
    def actual_call(self):
        return self._actual_call


class OversaturatedCall(MockifyAssertion):
    """Raised when mock with actions recorded using
    :meth:`mockify.Expectation.will_once` was called more times than
    expected and has all recorded actions already consumed.

    This exception can be avoided if you record repeated action to the end of
    expected action chain (using
    :meth:`mockify.Expectation.will_repeatedly`). However, it was added for a
    reason. For example, if your mock returns value of incorrect type (the
    default one), you'll result in production code errors instead of mock
    errors. And that can possibly be harder to debug.

    :param actual_call:
        The call that was made

    :param oversaturated_expectation:
        The expectation that was oversaturated
    """

    def __init__(self, actual_call, oversaturated_expectation):
        self._actual_call = actual_call
        self._oversaturated_expectation = oversaturated_expectation

    @_utils.log_unhandled_exceptions(logger)
    def __str__(self):
        builder = _utils.ErrorMessageBuilder()
        builder.append_line('Following expectation was oversaturated:')
        builder.append_line('')
        builder.append_location(self._oversaturated_expectation.expected_call.location)
        builder.append_line('Pattern:')
        builder.append_line('  {}', self._oversaturated_expectation.expected_call)
        builder.append_line('Expected:')
        builder.append_line('  {}', self._oversaturated_expectation.expected_call_count)
        builder.append_line('Actual:')
        builder.append_line('  oversaturated by {} at {} (no more actions)', self._actual_call, self._actual_call.location)
        return builder.build()

    @property
    def actual_call(self):
        return self._actual_call

    @property
    def oversaturated_expectation(self):
        return self._oversaturated_expectation


class Unsatisfied(MockifyAssertion):
    """Raised when unsatisfied expectations are present.

    This can only be raised by either :func:`mockify.satisfied` or
    :meth:`mockify.Session.done`. You'll not get this exception when mock is
    called.

    :param unsatisfied_expectations:
        List of all unsatisfied expectations found
    """

    def __init__(self, unsatisfied_expectations):
        self._unsatisfied_expectations = unsatisfied_expectations

    @_utils.log_unhandled_exceptions(logger)
    def __str__(self):
        builder = _utils.ErrorMessageBuilder()
        self.__append_title(builder)
        for expectation in self._unsatisfied_expectations:
            self.__append_expectation(builder, expectation)
        return builder.build()

    def __append_title(self, builder):
        if len(self._unsatisfied_expectations) > 1:
            builder.append_line('Following {} expectations are not satisfied:', len(self._unsatisfied_expectations))
        else:
            builder.append_line('Following expectation is not satisfied:')

    def __append_expectation(self, builder, expectation):
        builder.append_line('')
        builder.append_location(expectation.expected_call.location)
        builder.append_line('Pattern:')
        builder.append_line('  {}', expectation.expected_call)
        self.__append_action(builder, expectation)
        builder.append_line('Expected:')
        builder.append_line('  {}', expectation.expected_call_count)
        builder.append_line('Actual:')
        builder.append_line('  {}', expectation.actual_call_count)

    def __append_action(self, builder, expectation):
        action = expectation.next_action.format_message() if expectation.next_action is not None else None
        if action is not None:
            builder.append_line('Action:')
            builder.append_line('  {}', action)

    @property
    def unsatisfied_expectations(self):
        """List of unsatisfied expectations.

        .. versionadded:: 1.0
            Previously it was called ``expectations``.
        """
        return self._unsatisfied_expectations
