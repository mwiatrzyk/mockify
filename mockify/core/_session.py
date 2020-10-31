# ---------------------------------------------------------------------------
# mockify/core/_session.py
#
# Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import collections
import itertools
import warnings

from .. import exc
from . import _config
from ._expectation import Expectation


class Session:
    """A class providing core logic of connecting mock calls with recorded
    expectations.

    Sessions are created for each mock automatically, or can be created
    explicitly and then shared across multiple mocks. While mock classes can
    be seen as som kind of frontends that mimic behavior of various Python
    constructs, session instances are some kind of backends that receive
    :class:`mockify.Call` instances created by mocks during either mock call,
    or expectation recording.

    .. versionchanged:: 0.6
        Previously this was named **Registry**.
    """

    def __init__(self):
        self._unordered_expectations = []
        self._ordered_expectations = collections.deque()
        self._ordered_expectations_enabled_for = set()
        self._config = _config.Config(
            {
                'uninterested_call_strategy': _config.Enum(
                    ['fail', 'warn', 'ignore'], default='fail'
                ),
                'expectation_class': _config.Type(
                    Expectation, default=Expectation
                ),
            }
        )

    @property
    def config(self):
        """A dictionary-like object for configuring sessions.

        Following options are currently available:

        ``'expectation_class'``
            Can be used to override expectation class used when expectations
            are recorded.

            By default, this is :class:`mockify.Expectation`, and there is a
            requirement that custom class must inherit from original one.

        ``'uninterested_call_strategy'``
            Used to set a way of processing so called **unexpected calls**,
            i.e. calls to mocks that has no expectations recorded. Following
            values are supported:

            ``'fail'``
                This is default option.

                When mock is called unexpectedly,
                :exc:`mockify.exc.UninterestedCall` exception is raised and
                test is terminated.

            ``'warn'``
                Instead of raising exception,
                :exc:`mockify.exc.UninterestedCallWarning` warning is issued,
                and test continues.

            ``'ignore'``
                Unexpected calls are silently ignored.
        """
        return self._config

    def __call__(self, actual_call):
        """Trigger expectation matching *actual_call* received from mock
        being called.

        This method is called on every mock call and basically all actual
        call processing takes place here. Values returned or exceptions
        raised by this method are also returned or raised by mock.

        :param actual_call:
            Instance of :class:`mockify.Call` class created by calling mock.
        """
        if self._is_ordered(actual_call):
            return self.__call_ordered(actual_call)
        return self.__call_unordered(actual_call)

    def __call_ordered(self, actual_call):
        head = self._ordered_expectations[0]
        if head.expected_call != actual_call:
            raise exc.UnexpectedCallOrder(actual_call, head.expected_call)
        try:
            return head(actual_call)
        finally:
            if head.is_satisfied():
                self._ordered_expectations.popleft()

    def __call_unordered(self, actual_call):
        found_by_call = [
            x for x in self.expectations() if x.expected_call == actual_call
        ]
        if not found_by_call:
            return self.__handle_uninterested_call(actual_call)
        for expectation in found_by_call:
            if not expectation.is_satisfied():
                return expectation(actual_call)
        return found_by_call[-1](
            actual_call
        )  # Oversaturate last found if all are satisfied

    def __handle_uninterested_call(self, actual_call):
        uninterested_call_strategy = self._config.get(
            'uninterested_call_strategy'
        )
        if uninterested_call_strategy == 'fail':
            self.__handle_uninterested_call_using_fail_strategy(actual_call)
        elif uninterested_call_strategy == 'ignore':
            pass
        elif uninterested_call_strategy == 'warn':
            warnings.warn(str(actual_call), exc.UninterestedCallWarning)

    def __handle_uninterested_call_using_fail_strategy(self, actual_call):
        found_by_name = [
            x.expected_call for x in self.expectations()
            if x.expected_call.name == actual_call.name
        ]
        if not found_by_name:
            raise exc.UninterestedCall(actual_call)
        raise exc.UnexpectedCall(actual_call, found_by_name)

    def expectations(self):
        """An iterator over all expectations recorded in this session.

        Yields :class:`mockify.Expectation` instances.
        """
        return itertools.chain(
            self._unordered_expectations, self._ordered_expectations
        )

    def expect_call(self, expected_call):
        """Called by mock when expectation is recorded on it.

        This method creates expectation object, adds it to the list of
        expectations, and returns.

        :rtype: mockify.Expectation

        :param expected_call:
            Instance of :class:`mockify.Call` created by mock when
            **expect_call()** was called on it.

            Represents parameters the mock is expected to be called with.
        """
        expectation_class = self.config['expectation_class']
        expectation = expectation_class(expected_call)
        self._unordered_expectations.append(expectation)
        return expectation

    def assert_satisfied(self):
        """Check if all registered expectations are satisfied.

        This works exactly the same as :func:`mockify.assert_satisfied`, but
        for given session only. Can be used as a replacement for any other
        checks if one global session object is used.
        """
        unsatisfied_expectations = [
            x for x in self.expectations() if not x.is_satisfied()
        ]
        if unsatisfied_expectations:
            raise exc.Unsatisfied(unsatisfied_expectations)

    def enable_ordered(self, names):
        """Mark expectations matching given mock *names* as **ordered**, so
        they will have to be resolved in their declaration order.

        This is used internally by :func:`mockify.ordered`.
        """
        self._ordered_expectations_enabled_for = set(names)
        unordered_expectations = list(self._unordered_expectations)
        self._unordered_expectations = []
        self._ordered_expectations = collections.deque()
        for expectation in unordered_expectations:
            if self._is_ordered(expectation.expected_call):
                self._ordered_expectations.append(expectation)
            else:
                self._unordered_expectations.append(expectation)

    def disable_ordered(self):
        """Called by :func:`mockify.ordered` when processing of ordered
        expectations is done.

        Moves any remaining expectations back to the **unordered** storage,
        so they will be later displayed as unsatisfied.
        """
        if self._ordered_expectations:
            self._unordered_expectations.extend(self._ordered_expectations)
        self._ordered_expectations = []
        self._ordered_expectations_enabled_for = set()

    def _is_ordered(self, call):
        return call.name in self._ordered_expectations_enabled_for
