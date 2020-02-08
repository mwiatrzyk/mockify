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
from ..cardinality import ActualCallCount, Exactly, AtLeast


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

    class _ProxyBase:

        def __repr__(self):
            return repr(self._expectation)

        @property
        def _expectation(self):
            return self.__expectation()

        @_expectation.setter
        def _expectation(self, value):
            self.__expectation = weakref.ref(value)

        def _wrap_expected_count(self, expected_count):
            if isinstance(expected_count, int):
                return Exactly(expected_count)
            else:
                return expected_count

    class _DefaultProxy(_ProxyBase):

        def __init__(self, expectation):
            self._actual_count = ActualCallCount(0)
            self._expected_count = Exactly(1)
            self._expectation = expectation
            self._next_action = None

        def __call__(self, call):
            self._actual_count += 1

        def _is_satisfied(self):
            return self._expected_count.match(self._actual_count)

        @property
        def _actual_call_count(self):
            return self._actual_count

        @property
        def _expected_call_count(self):
            return self._expected_count

    class _TimesProxy(_ProxyBase):

        def __init__(self, expected_count, expectation):
            self._expectation = expectation
            self._actual_count = ActualCallCount(0)
            self._expected_count = self._wrap_expected_count(expected_count)
            self._next_action = None

        def __call__(self, call):
            self._actual_count += 1

        def _is_satisfied(self):
            return self._expected_count.match(self._actual_count)

        @property
        def _actual_call_count(self):
            return self._actual_count

        @property
        def _expected_call_count(self):
            return self._expected_count

    class _ActionProxy(_ProxyBase):

        def __init__(self, action, expectation):
            self._actions = collections.deque([action])
            self._expectation = expectation
            self._expected_count = Exactly(1)
            self._actual_count = ActualCallCount(0)
            self._next_proxy = None

        def __call__(self, call):
            if not self._is_satisfied():
                return self.__invoke_action(call)
            elif self._next_proxy is not None:
                return self._next_proxy(call)
            else:
                return self.__invoke_action(call)

        def __invoke_action(self, call):
            if not self._actions:
                raise exc.OversaturatedCall(call, self._expectation)
            else:
                self._actual_count += 1
                try:
                    return self._actions[0](call)
                finally:
                    self._actions.popleft()

        def _is_satisfied(self):
            return self._expected_count.match(self._actual_count)

        @property
        def _actual_call_count(self):
            if self._next_proxy is None:
                return self._actual_count
            else:
                return self._next_proxy._actual_call_count

        @property
        def _expected_call_count(self):
            if self._next_proxy is None:
                return self._expected_count
            else:
                return self._next_proxy._expected_call_count

        @property
        def _next_action(self):
            if self._actions:
                return self._actions[0]
            elif self._next_proxy is not None:
                return self._next_proxy._next_action

        def will_once(self, action):
            if self._actions[-1] == action:
                self._actions.append(action)
                self._expected_count = Exactly(len(self._actions))
                return self
            else:
                self._next_proxy = tmp = Expectation._ActionProxy(action, self._expectation)
                return tmp

        def will_repeatedly(self, action):
            expected_call_count = None
            if self._actions and self._actions[-1] == action:
                expected_call_count = AtLeast(len(self._actions))
            self._next_proxy = tmp = Expectation.\
                _RepeatedActionProxy(action, self._expectation, expected_call_count)
            return tmp

    class _RepeatedActionProxy(_ProxyBase):

        def __init__(self, action, expectation, expected_call_count=None):
            self._action = action
            self._expectation = expectation
            self._expected_count = expected_call_count or AtLeast(0)
            self._actual_count = ActualCallCount(0)
            self._next_proxy = None

        def __call__(self, call):
            if not self._is_satisfied():
                return self.__invoke_action(call)
            elif self._next_proxy is not None:
                return self._next_proxy(call)
            else:
                return self.__invoke_action(call)

        def __invoke_action(self, call):
            self._actual_count += 1
            return self._action(call)

        def _is_satisfied(self):
            return self._expected_count.match(self._actual_count)

        def _format_action(self):
            return str(self._action)

        def _format_expected(self, minimal=None):
            minimal = minimal or 0
            if self._next_proxy is None:
                if self._expected_count is not None:
                    return self._expected_count.adjust_minimal_by(minimal).format_expected()
                elif minimal > 0:
                    return AtLeast(minimal).format_expected()
            elif self._expected_count is not None:
                return self._next_proxy._format_expected(
                    minimal=minimal + self._expected_count.minimal)

        @property
        def _actual_call_count(self):
            return self._actual_count

        @property
        def _expected_call_count(self):
            return self._expected_count

        @property
        def _next_action(self):
            return self._action

        def times(self, expected_count):
            self._expected_count = self._wrap_expected_count(expected_count)
            return self

        # TODO: these will have to be done by another proxy, returned once you
        # call times() on your mock. Without that, these actions will never get
        # executed, so expectation will be broken...

        # def will_once(self, action):
        #     self._next_proxy = tmp = Expectation._ActionProxy(action, self._expectation)
        #     return tmp

        # def will_repeatedly(self, action):
        #     self._next_proxy = tmp = self.__class__(action, self._expectation)
        #     return tmp

    def __init__(self, expected_call):
        self._expected_call = expected_call
        self._next_proxy = self._DefaultProxy(self)

    def __repr__(self):
        return "<mockify.{}: {}>".format(self.__class__.__name__, self._expected_call)

    def __call__(self, call):
        """Call this expectation object.

        If given ``call`` object does not match :attr:`expected_call` then this
        method will raise :exc:`TypeError` exception.

        Otherwise, total call count is increased by one and:

            * if actions are recorded, then next action is executed and its
              result returned or :exc:`mockify.exc.OversaturatedCall` exception
              is raised if there are no more actions

            * if there are no actions recorded, just ``None`` is returned
        """
        assert self._expected_call == call
        return self._next_proxy(call)

    def is_satisfied(self):
        """Check if this expectation is satisfied.

        Expectation object is satisfied if and only if:

        * total number of calls is not exceeding expected number of calls,
        * all actions (if any were recorded) are **consumed**.

        :rtype: bool
        """
        tmp = self._next_proxy
        while tmp is not None:
            if not tmp._is_satisfied():
                return False
            tmp = getattr(tmp, '_next_proxy', None)
        return True

    def times(self, cardinality):
        """Set expected number or range of call counts.

        Following values are possible:

        * integer number (for setting expected call count to fixed value),
        * instance of :class:`mockify.cardinality.ExpectedCallCount` (for
          setting expected call count to **ranged** value).

        See :ref:`setting-expected-call-count` tutorial section for more
        details.
        """
        self._next_proxy = tmp = self._TimesProxy(cardinality, self)
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
        self._next_proxy = tmp = self._ActionProxy(action, self)
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
        self._next_proxy = tmp = self._RepeatedActionProxy(action, self)
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
        return self._next_proxy._actual_call_count

    @property
    def expected_call_count(self):
        """Return object representing expected number of mock calls.

        Like :attr:`actual_call_count`, this varies depending on internal
        expectation object state.

        :rtype: mockify.cardinality.ExpectedCallCount
        """
        return self._next_proxy._expected_call_count

    @property
    def next_action(self):
        """Return action to be executed when this expectation receives
        another call or ``None`` if there are no (more) actions.

        :rtype: mockify.actions.Action
        """
        return self._next_proxy._next_action
