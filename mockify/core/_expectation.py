# ---------------------------------------------------------------------------
# mockify/core/_expectation.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

# pylint: disable=missing-module-docstring

import collections
from enum import Enum

from mockify import _utils, exc
from mockify.abc import ICall, IExpectation
from mockify.actions import Return
from mockify.cardinality import ActualCallCount, AtLeast, Exactly

__all__ = export = _utils.ExportList()  # pylint: disable=invalid-all-format


class _ActionType(Enum):
    DEFAULT = "default"
    SINGLE = "single"
    REPEATED = "repeated"


@export
class Expectation(IExpectation):
    """Default implementation of the :class:`mockify.abc.IExpectation`
    interface.

    Instances of this class are created and returned when expectations are
    recorded on mocks.

    Here's an example:

    .. doctest::

        >>> from mockify.mock import Mock
        >>> mock = Mock('mock')
        >>> mock.expect_call(1, 2)
        <mockify.core.Expectation: mock(1, 2)>

    :param expected_call:
        Instance of :class:`mockify.abc.ICall` object that was created during
        expectation recording.

        .. note::
            Value of :attr:`mockify.abc.ICall.location` property of given call
            object will point to the place in user's test code where
            ``expect_call(...)`` method was called.
    """

    def __init__(self, expected_call: ICall):
        self._expected_call = expected_call
        self._action_store = self._ActionStore()
        self._action_store.add(self._ActionProxy(_ActionType.DEFAULT, Return(None), Exactly(1)))

    def __repr__(self):
        return "<mockify.core.{}: {}>".format(self.__class__.__name__, self._expected_call)

    def __call__(self, actual_call: ICall):
        """Consume this expectation object.

        This method requires given *actual_call* object to satisfy following
        condition::

            self.expected_call == actual_call

        In other words, given *actual_call* must be equal to current
        :attr:`expected_call` object, as consuming expectation with a
        non-matching actuall call does not make sense and is considered as a
        bug.

        :param actual_call:
            Instance of :class:`mockify.abc.ICall` object that was created when
            corresponding mock was called.

            .. note::
                Value of :attr:`mockify.abc.ICall.location` property of given
                call object will point to the place in user's tested code where
                the mocked method or function was called.
        """
        assert self.expected_call == actual_call
        return self._action_store(actual_call, self)

    def is_satisfied(self):
        """See :meth:`mockify.abc.IExpectation.is_satisfied`."""
        return self.expected_call_count.match(self.actual_call_count)

    def times(self, cardinality):
        """See :meth:`mockify.abc.IExpectation.times`."""
        return self._Times(self, cardinality)

    def will_once(self, action):
        """See :meth:`mockify.abc.IExpectation.will_once`."""
        if self._action_store[0].type_ == _ActionType.DEFAULT:
            self._action_store.pop()
        return self._WillOnce(self, action)

    def will_repeatedly(self, action):
        """See :meth:`mockify.abc.IExpectation.will_repeatedly`."""
        if self._action_store[0].type_ == _ActionType.DEFAULT:
            self._action_store.pop()
        return self._WillRepeatedly(self, action)

    @property
    def expected_call(self) -> ICall:
        """Returns **expected call** object assigned to this expectation.

        This is used by Mockify's internals to find expectations that match
        given **actual call** object.
        """
        return self._expected_call

    @property
    def actual_call_count(self) -> int:
        """Number of matching calls this expectation object received so far.

        This is relative value; if one action expires and another one is
        started to be executed, then the counter starts counting from 0
        again. Thanks to this you'll receive information about actual action
        execution count. If your expectation does not use :meth:`will_once`
        or :meth:`will_repeatedly`, then this counter will return total
        number of calls.

        .. versionadded:: 0.6
        """
        return self._action_store.actual_call_count

    @property
    def expected_call_count(self):
        """Return object representing expected number of mock calls.

        Like :attr:`actual_call_count`, this varies depending on internal
        expectation object state.

        :rtype: mockify.cardinality.ExpectedCallCount
        """
        return self._action_store.expected_call_count

    @property
    def action(self):
        """Return action to be executed when this expectation receives
        another call or ``None`` if there are no (more) actions.

        :rtype: mockify.actions.Action
        """
        return self._action_store.action

    class _ActionProxy:
        # pylint: disable=missing-function-docstring

        def __init__(self, type_, action, cardinality):
            self._type = type_
            self._action = action
            self._expected_call_count = self._wrap_cardinality(cardinality)
            self._actual_call_count = 0

        def __call__(self, actual_call):
            self._actual_call_count += 1
            return self._action(actual_call)

        @staticmethod
        def _wrap_cardinality(cardinality):
            if isinstance(cardinality, int):
                return Exactly(cardinality)
            return cardinality

        @property
        def type_(self):
            return self._type

        @property
        def action(self):
            return self._action

        @property
        def actual_call_count(self):
            return self._actual_call_count

        @property
        def expected_call_count(self):
            return self._expected_call_count

        def times(self, cardinality):
            self._expected_call_count = self._wrap_cardinality(cardinality)

        def is_satisfied(self):
            return self._expected_call_count.match(self.actual_call_count)

    class _ActionStore:
        # pylint: disable=missing-function-docstring

        def __init__(self):
            self._actions = collections.deque()

        def __call__(self, actual_call, expectation):
            for action in self._actions:
                if not action.is_satisfied():
                    return action(actual_call)
            if self._actions[-1].type_ != _ActionType.SINGLE:
                return self._actions[-1](actual_call)
            raise exc.OversaturatedCall(actual_call, expectation)

        def __getitem__(self, index):
            return self._actions[index]

        def add(self, action_proxy):
            self._actions.append(action_proxy)

        def pop(self):
            self._actions.popleft()

        @property
        def actual_call_count(self):
            return ActualCallCount(sum((x.actual_call_count for x in self._actions)))

        @property
        def expected_call_count(self):
            if self._actions[0].type_ == _ActionType.DEFAULT:
                return self._actions[0].expected_call_count
            minimal = sum(map(lambda x: x.type_ == _ActionType.SINGLE, self._actions))
            if self._actions[-1].type_ != _ActionType.REPEATED:
                return Exactly(minimal)
            return self._actions[-1].expected_call_count.adjust_minimal(minimal)

        @property
        def action(self):
            for action_proxy in self._actions:
                if not action_proxy.is_satisfied() and action_proxy.type_ != _ActionType.DEFAULT:
                    return action_proxy.action
            return None

    class _Mutation:
        # pylint: disable=too-few-public-methods
        _expectation = None

        def __repr__(self):
            return repr(self._expectation)

    class _Times(_Mutation):
        # pylint: disable=too-few-public-methods

        def __init__(self, expectation, cardinality):
            self._expectation = expectation
            expectation._action_store[0].times(cardinality)

    class _WillOnce(_Mutation, IExpectation.IWillOnceMutation):
        # pylint: disable=missing-function-docstring

        def __init__(self, expectation, action):
            self._expectation = expectation
            action_store = expectation._action_store
            action_store.add(expectation._ActionProxy(_ActionType.SINGLE, action, Exactly(1)))

        def will_once(self, action):
            return self.__class__(self._expectation, action)

        def will_repeatedly(self, action):
            return self._expectation.will_repeatedly(action)

    class _WillRepeatedly(_Mutation, IExpectation.IWillRepeatedlyMutation):
        # pylint: disable=missing-function-docstring
        # pylint: disable=too-few-public-methods

        def __init__(self, expectation, action):
            self._expectation = expectation
            self._action_proxy = expectation._ActionProxy(_ActionType.REPEATED, action, AtLeast(0))
            self._action_store.add(self._action_proxy)

        @property
        def _action_store(self):
            return self._expectation._action_store  # pylint: disable=protected-access

        def times(self, cardinality):
            self._action_proxy.times(cardinality)
