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

from mockify.interface import IExpectation

from .. import exc
from ..actions import Return
from ..cardinality import ActualCallCount, AtLeast, Exactly


class _ActionType(Enum):
    DEFAULT = 'default'
    SINGLE = 'single'
    REPEATED = 'repeated'


class Expectation(IExpectation):
    """An class representing single expectation.

    Instances of this class are created and returned by factory
    **expect_call()** method you will use to record expectations on your
    mocks:

    .. doctest::

        >>> from mockify.mock import Mock
        >>> mock = Mock('mock')
        >>> mock.expect_call(1, 2)
        <mockify.Expectation: mock(1, 2)>

    :param expected_call:
        Instance of :class:`Call` class containing parameters passed to
        **expect_call()** factory method that created this expectation object.
    """

    def __init__(self, expected_call):
        self._expected_call = expected_call
        self._action_store = self._ActionStore()
        self._action_store.add(
            self._ActionProxy(_ActionType.DEFAULT, Return(None), Exactly(1))
        )

    def __repr__(self):
        return "<mockify.{}: {}>".format(
            self.__class__.__name__, self._expected_call
        )

    def __call__(self, actual_call):
        """Call this expectation object.

        If given ``call`` object does not match :attr:`expected_call` then this
        method will raise :exc:`TypeError` exception.

        Otherwise, total call count is increased by one and:

            * if actions are recorded, then next action is executed and its
              result returned or :exc:`mockify.exc.OversaturatedCall` exception
              is raised if there are no more actions

            * if there are no actions recorded, just ``None`` is returned
        """
        assert self.expected_call == actual_call
        return self._action_store(actual_call, self)

    def is_satisfied(self):
        """Check if this expectation is satisfied.

        Expectation object is satisfied if and only if:

        * total number of calls is not exceeding expected number of calls,
        * all actions (if any were recorded) are **consumed**.

        :rtype: bool
        """
        return self.expected_call_count.match(self.actual_call_count)

    def times(self, cardinality):
        """Set expected number or range of call counts.

        Following values are possible:

        * integer number (for setting expected call count to fixed value),
        * instance of :class:`mockify.cardinality.ExpectedCallCount` (for
          setting expected call count to **ranged** value).

        See :ref:`setting-expected-call-count` tutorial section for more
        details.
        """
        return self._Times(self, cardinality)

    def will_once(self, action):
        """Append next action to be executed when this expectation object
        receives a call.

        Once this method is called, it returns special proxy object that you
        can use to mutate this expectation even further by calling one of
        given methods on that proxy:

        * **will_once()** (this one again),
        * **will_repeatedly()** (see :meth:`will_repeatedly`).

        Thanks to that you can record so called **action chains** (see
        :ref:`recording-action-chains` for more details).

        This method can be called with any action object from
        :mod:`mockify.actions` as an argument.
        """
        if self._action_store[0].type_ == _ActionType.DEFAULT:
            self._action_store.pop()
        return self._WillOnce(self, action)

    def will_repeatedly(self, action):
        """Attach so called **repeated action** to be executed when this
        expectation is called.

        Unlike single actions, recorded with :meth:`will_once`, repeated
        actions are by default executed any number of times, including zero
        (see :ref:`recording-repeated-actions` for more details).

        Once this method is called, it returns a proxy object you can use to
        adjust repeated action even more by calling one of following methods:

        * **times()**, used to record repeated action call count limits (see
          :meth:`times`).

        This method accepts actions defined in :mod:`mockify.actions` module.
        """
        if self._action_store[0].type_ == _ActionType.DEFAULT:
            self._action_store.pop()
        return self._WillRepeatedly(self, action)

    @property
    def expected_call(self):
        """Returns *expected_call* parameter passed during construction.

        This is used when this expectation is compared with
        :class:`mockify.core.Call` object representing **actual call**, to
        find expectations matching that call.

        :rtype: mockify.core.Call
        """
        return self._expected_call

    @property
    def actual_call_count(self):
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
            return ActualCallCount(
                sum((x.actual_call_count for x in self._actions))
            )

        @property
        def expected_call_count(self):
            if self._actions[0].type_ == _ActionType.DEFAULT:
                return self._actions[0].expected_call_count
            minimal = sum(
                map(lambda x: x.type_ == _ActionType.SINGLE, self._actions)
            )
            if self._actions[-1].type_ != _ActionType.REPEATED:
                return Exactly(minimal)
            return self._actions[-1].expected_call_count.adjust_minimal(minimal)

        @property
        def action(self):
            for action_proxy in self._actions:
                if not action_proxy.is_satisfied() and\
                   action_proxy.type_ != _ActionType.DEFAULT:
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
            action_store.add(
                expectation._ActionProxy(
                    _ActionType.SINGLE, action, Exactly(1)
                )
            )

        def will_once(self, action):
            return self.__class__(self._expectation, action)

        def will_repeatedly(self, action):
            return self._expectation.will_repeatedly(action)

    class _WillRepeatedly(_Mutation, IExpectation.IWillRepeatedlyMutation):
        # pylint: disable=missing-function-docstring
        # pylint: disable=too-few-public-methods

        def __init__(self, expectation, action):
            self._expectation = expectation
            self._action_proxy = expectation._ActionProxy(
                _ActionType.REPEATED, action, AtLeast(0)
            )
            self._action_store.add(self._action_proxy)

        @property
        def _action_store(self):
            return self._expectation._action_store  # pylint: disable=protected-access

        def times(self, cardinality):
            self._action_proxy.times(cardinality)
