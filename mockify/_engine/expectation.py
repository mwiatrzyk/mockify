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
    """Class representing single expectation.

    Instances of this class are normally created by registry objects using
    :meth:`Registry.expect_call` method. Each instance of this class is
    correlated with exactly one :class:`mockify.engine.Call` object
    representing expected mock call pattern.

    After :class:`Expectation` object is created by call to some
    ``expect_call`` method, it can be mutated using following methods:

        * :meth:`times`
        * :meth:`will_once`
        * :meth:`will_repeatedly`

    :param call:
        Instance of :class:`mockify.engine.Call` representing expected mock
        call pattern

    :param filename:
        File name were this expectation was created

        .. deprecated:: 0.6
            This parameter is no longer used and will be removed in one
            of upcoming releases.

    :param lineno:
        Line number where this expectation was created

        .. deprecated:: 0.6
            This parameter is no longer used and will be removed in one
            of upcoming releases.
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

        def will_once(self, action):
            self._next_proxy = tmp = Expectation._ActionProxy(action, self._expectation)
            return tmp

        def will_repeatedly(self, action):
            self._next_proxy = tmp = self.__class__(action, self._expectation)
            return self

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

    @property
    def expected_call(self):
        """Instance of :class:`mockify.engine.Call` representing expected mock
        call pattern.

        This basically is exactly the same :class:`Call` object as was passed
        to :class:`Expectation` constructor.
        """
        return self._expected_call

    def match(self, call):
        """Check if :attr:`expected_call` matches ``call``."""
        return self._expected_call == call

    def is_satisfied(self):
        """Check if this expectation is satisfied."""
        tmp = self._next_proxy
        while tmp is not None:
            if not tmp._is_satisfied():
                return False
            tmp = getattr(tmp, '_next_proxy', None)
        return True

    def times(self, expected_count):
        """Record how many times this expectation is expected to be called.

        :param expected_count:
            Expected call count.

            This can be either integer number (exact call count) or instance of
            one of classes from :mod:`mockify.times` module.
        """
        self._next_proxy = tmp = self._TimesProxy(expected_count, self)
        return tmp

    def will_once(self, action):
        """Attach action to be executed when this expectation gets consumed.

        This method can be used several times, making action chains. Once
        expectation is consumed, next action is executed and removed from the
        list. If there are no more actions, another call will fail with
        :exc:`mockify.exc.OversaturatedCall` exception.

        After this method is used, you can also use :meth:`will_repeatedly` to
        record repeated action that will get executed after all single actions
        are consumed.

        :param action:
            Action to be executed.

            See :mod:`mockify.actions` for details.
        """
        self._next_proxy = tmp = self._ActionProxy(action, self)
        return tmp

    def will_repeatedly(self, action):
        """Attach repeated action to be executed when this expectation is called.

        This method is used to record one action that gets executed each time
        this expectation object is called. By default, when repeated action is
        recorded, expectation can be called any number of times (including
        zero).

        After setting repeated action, you can also set expected call count
        using :meth:`times`.

        :param action:
            Action to be executed.

            See :mod:`mockify.actions` for details.
        """
        self._next_proxy = tmp = self._RepeatedActionProxy(action, self)
        return tmp

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
        """Return :class:`mockify.cardinality.Cardinality` instance
        representing expected number of mock calls."""
        return self._next_proxy._expected_call_count

    @property
    def next_action(self):
        """Return :class:`mockify.actions.Action` object representing next
        action to be executed or ``None`` if there are no (more) actions
        defined for this expectation object."""
        return self._next_proxy._next_action
