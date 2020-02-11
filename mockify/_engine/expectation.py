# ---------------------------------------------------------------------------
# mockify/_engine/expectation.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import weakref
import warnings
import collections

from .. import exc, _utils
from .call import Call
from ..cardinality import ActualCallCount, ExpectedCallCount, Exactly, AtLeast


class Expectation:
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
        self._state = self._InitialState(self)

    def __repr__(self):
        return "<mockify.{}: {}>".format(self.__class__.__name__, self._expected_call)

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
        return self._state(actual_call)

    def is_satisfied(self):
        """Check if this expectation is satisfied.

        Expectation object is satisfied if and only if:

        * total number of calls is not exceeding expected number of calls,
        * all actions (if any were recorded) are **consumed**.

        :rtype: bool
        """
        return self._state._is_satisfied()

    def times(self, cardinality):
        """Set expected number or range of call counts.

        Following values are possible:

        * integer number (for setting expected call count to fixed value),
        * instance of :class:`mockify.cardinality.ExpectedCallCount` (for
          setting expected call count to **ranged** value).

        See :ref:`setting-expected-call-count` tutorial section for more
        details.
        """
        self._state = tmp = self._TimedState(self, cardinality)
        return tmp

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
        self._state = tmp = self._ActionState(self, action)
        return tmp

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
        self._state = tmp = self._RepeatedActionState(self, action)
        return tmp

    @property
    def expected_call(self):
        """Returns *expected_call* parameter passed during construction.

        This is used when this expectation is compared with :class:`Call`
        object representing **actual call**, to find expectations matching
        that call.

        :rtype: Call
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

        .. versionadded:: 1.0
        """
        return self._state._actual_call_count

    @property
    def expected_call_count(self):
        """Return object representing expected number of mock calls.

        Like :attr:`actual_call_count`, this varies depending on internal
        expectation object state.

        :rtype: mockify.cardinality.ExpectedCallCount
        """
        return self._state._expected_call_count

    @property
    def next_action(self):
        """Return action to be executed when this expectation receives
        another call or ``None`` if there are no (more) actions.

        :rtype: mockify.actions.Action
        """
        return self._state._action

    class _State:
        _action = None

        def __repr__(self):
            return repr(self._expectation)

        @property
        def _expectation(self):
            return self.__expectation()

        @_expectation.setter
        def _expectation(self, value):
            self.__expectation = weakref.ref(value)

        def _wrap_cardinality(self, cardinality):
            if not isinstance(cardinality, ExpectedCallCount):
                return Exactly(cardinality)
            else:
                return cardinality

    class _InitialState(_State):

        def __init__(self, expectation):
            self._expectation = expectation
            self._expected_call_count = Exactly(1)
            self._actual_call_count = ActualCallCount(0)

        def __call__(self, actual_call):
            self._actual_call_count += 1

        def _is_satisfied(self):
            return self._expected_call_count.match(self._actual_call_count)

    class _TimedState(_State):

        def __init__(self, expectation, cardinality):
            self._expectation = expectation
            self._expected_call_count = self._wrap_cardinality(cardinality)
            self._actual_call_count = ActualCallCount(0)

        def __call__(self, actual_call):
            self._actual_call_count += 1

        def _is_satisfied(self):
            return self._expected_call_count.match(self._actual_call_count)

    class _ActionState(_State):

        def __init__(self, expectation, action):
            self._expectation = expectation
            self._actions = [action]
            self._action_index = 0
            self._next_state = None

        def __call__(self, actual_call):
            action = self.__get_action()
            self._action_index += 1
            if action is None:
                if self._next_state is None:
                    raise exc.OversaturatedCall(actual_call, self._expectation)
                else:
                    return self._next_state(actual_call)
            else:
                return action(actual_call)

        def __get_action(self):
            try:
                return self._actions[self._action_index]
            except IndexError:
                pass

        @property
        def _action(self):
            try:
                return self._actions[self._action_index]
            except IndexError:
                if self._next_state is not None:
                    return self._next_state._action

        @property
        def _actual_call_count(self):
            return ActualCallCount(self._action_index)

        @property
        def _expected_call_count(self):
            if self._next_state is None:
                return Exactly(len(self._actions))
            else:
                return self._next_state._expected_call_count

        def _is_satisfied(self):
            return self._expected_call_count.match(self._action_index)

        def will_once(self, action):
            self._actions.append(action)
            return self

        def will_repeatedly(self, action):
            self._next_state = tmp =\
                Expectation._RepeatedActionState(
                    self._expectation, action, self._actual_call_count.value, len(self._actions))
            return tmp

    class _RepeatedActionState(_State):

        def __init__(self, expectation, action, actual_count=0, expected_count=0):
            self._expectation = expectation
            self._action = action
            self._actual_call_count = ActualCallCount(actual_count)
            self._expected_call_count = AtLeast(expected_count)

        def __call__(self, actual_call):
            try:
                return self._action(actual_call)
            finally:
                self._actual_call_count += 1

        def _is_satisfied(self):
            return self._expected_call_count.match(self._actual_call_count.value)

        def times(self, cardinality):
            self._expected_call_count =\
                self._wrap_cardinality(cardinality).\
                adjust_minimal(self._expected_call_count.minimal)
