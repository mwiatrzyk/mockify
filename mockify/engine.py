# ---------------------------------------------------------------------------
# mockify/engine.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------

"""This module contains set of classes that provides backend mechanism for
storing and tracking call expectations."""

import weakref
import warnings
import itertools
import traceback
import collections

from mockify import exc, _utils
from mockify.times import Exactly, AtLeast


def _wrap_expected_count(expected_count):
    if isinstance(expected_count, int):
        return Exactly(expected_count)
    else:
        return expected_count


class Call:
    """Binds mock name with arguments it was called with or it is expected to
    be called with.

    Call objects are created in mock frontends (like
    :class:`mockify.mock.function.Function` mock class) by methods
    ``expected_call`` and ``__call__`` by simply passing their argument to
    :class:`Call` constructor.

    Instances of this class are comparable. Two :class:`Call` objects are equal
    if and only if all attributes (``name``, ``args`` and ``kwargs``) are the
    same. For example:

        >>> Call('foo') == Call('foo')
        True
        >>> Call('foo') != Call('bar')
        True
        >>> Call('foo', (1, 2), {'c': 3}) == Call('foo', (1, 2), {'c': 3})
        True

    Call objects can also be created with use of **matchers**, for example
    :class:`mockify.matchers.Any`, that will match any value:

        >>> from mockify.matchers import _
        >>> Call('foo', (_, _)) == Call('foo', (1, 2))
        True
        >>> Call('foo', (_, _)) == Call('foo', (3, 4))
        True

    :param name:
        Function or method name.

    :param args:
        Positional arguments

    :param kwargs:
        Named arguments
    """

    def __init__(self, name, args=None, kwargs=None):
        self._name = name
        self._args = args
        self._kwargs = kwargs

    def __str__(self):
        args_gen = (repr(x) for x in (self._args or tuple()))
        kwargs_gen = ("{}={!r}".format(k, v) for k, v in sorted((self._kwargs or {}).items()))
        all_gen = itertools.chain(args_gen, kwargs_gen)
        return "{}({})".format(self._name, ", ".join(all_gen))

    def __eq__(self, other):
        return self._name == other._name and\
            self._args == other._args and\
            self._kwargs == other._kwargs

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def name(self):
        """Mock name."""
        return self._name

    @property
    def args(self):
        """Mock positional args."""
        return self._args

    @property
    def kwargs(self):
        """Mock named args."""
        return self._kwargs


class Registry:
    """Acts like a database for :class:`Expectation` objects.

    This class is used as a backend for higher level mocking utilities (a.k.a.
    frontends), like :class:`mockify.mock.function.Function` mocking class. It
    provides methods to record, lookup and verifying of expectations.

    There can be many instances of registry classes, or one that can be shared
    between various mock frontends. For example, you can create one registry in
    setup code, then create various mocks inside your tests, to finally trigger
    :meth:`assert_satisfied` of that single registry in test's teardown code.
    Or you can just use frontends with their defaults. It is completely up to
    you.

    :param expectation_class:
        This is optional.

        Used to give custom subclass of :class:`Expectation` to be used inside
        this registry.

    :param uninterested_call_strategy:
        Setup the way how uninterested calls are treated.

        Following values are available:

            * *fail* - issue :exc:`mockify.exc.UninterestedCall` exception on
              each unexpectedly called mock (default)
            * *ignore* - do nothing with uninterested calls
            * *warn* - issue a warning on each uninterested call

        .. versionadded:: 0.4
    """

    def __init__(self,
            expectation_class=None,
            uninterested_call_strategy='fail'):
        self._expects = []
        self._expectation_class = expectation_class or Expectation
        self._uninterested_call_strategy = uninterested_call_strategy

    def __call__(self, call):
        """Call a mock.

        When this method is called, registry performs a lookup of matching
        unsatisfied expectations and calls first expectation found. If there
        are no matching expectation, then :exc:`mockify.exc.UninterestedCall`
        exception is raised. If there are matching expectations but all are
        satisfied, then last is called (making it oversaturated).

        :param call:
            Instance of :class:`mockify.engine.Call` class representing mock
            being called
        """
        matching_expects = list(filter(lambda x: x.match(call), self._expects))
        if not matching_expects:
            return self._handle_uninterested_call(call)
        for expect in matching_expects:
            if not expect.is_satisfied():
                return expect(call)
        else:
            return matching_expects[-1](call)

    def _handle_uninterested_call(self, call):
        if self._uninterested_call_strategy == 'fail':
            raise exc.UninterestedCall(call)
        elif self._uninterested_call_strategy == 'warn':
            warnings.warn('Uninterested mock called: {}'.format(str(call)))
        elif self._uninterested_call_strategy == 'ignore':
            return
        else:
            raise ValueError("Invalid uninterested call strategy: {}".format(self._uninterested_call_strategy))

    def expect_call(self, call, filename, lineno):
        """Register expectation.

        Returns instance of ``expectation_class`` (usually
        :class:`Expectation`) representing newly created expectation.

        :param call:
            Instance of :class:`mockify.engine.Call` class representing exact
            mock call or a pattern (if created with matchers) that is expected
            to be executed

        :param filename:
            Path to file were expectation is created

        :param lineno:
            Line number (inside ``filename``) where expectation is created
        """
        expect = self._expectation_class(call, filename, lineno)
        self._expects.append(expect)
        return expect

    def assert_satisfied(self, *names):
        """Assert that all expectations are satisfied.

        If there is at least one unsatisfied expectation, then this method will
        raise :exc:`mockify.exc.Unsatisfied` exception containing list of
        failed expectations.

        This method can be called as many times as you want.

        .. versionchanged:: 0.2

            Accepts names of mocks to check as positional args. If one or more
            names are given, then this method limits checking only to mocks of
            matching names.
        """
        unsatisfied = []
        keyfunc = lambda x: not names or x.expected_call.name in names
        for expect in filter(keyfunc, self._expects):
            if not expect.is_satisfied():
                unsatisfied.append(expect)
        if unsatisfied:
            raise exc.Unsatisfied(unsatisfied)


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

    :param lineno:
        Line number where this expectation was created
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

    class _DefaultProxy(_ProxyBase):

        def __init__(self, expectation):
            self._actual_count = 0
            self._expectation = expectation

        def __call__(self, call):
            self._actual_count += 1

        def _is_satisfied(self):
            return self._actual_count == 1

        def _format_expected(self):
            return _utils.format_expected_call_count(1)

    class _TimesProxy(_ProxyBase):

        def __init__(self, expected_count, expectation):
            self._actual_count = 0
            self._expectation = expectation
            self._expected_count = _wrap_expected_count(expected_count)

        def __call__(self, call):
            self._actual_count += 1

        def _is_satisfied(self):
            return self._expected_count.is_satisfied(self._actual_count)

        def _format_expected(self):
            return self._expected_count.format_expected()

    class _ActionProxy(_ProxyBase):

        def __init__(self, action, expectation):
            self._actions = collections.deque([action])
            self._expectation = expectation
            self._expected_count = Exactly(1)
            self._actual_count = 0
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
            if not self._actions:
                raise exc.OversaturatedCall(self._expectation, call)
            else:
                return self.__trigger_next(call)

        def __trigger_next(self, call):
            try:
                return self._actions[0](call)
            finally:
                self._actions.popleft()

        def _is_satisfied(self):
            return self._expected_count.is_satisfied(self._actual_count)

        def _format_action(self):
            if self._actions:
                return str(self._actions[0])
            elif self._next_proxy is not None:
                return self._next_proxy._format_action()

        def _format_expected(self, minimal=None):
            minimal = minimal or 0
            if self._next_proxy is None:
                return self._expected_count.adjust_by(minimal).format_expected()
            else:
                return self._next_proxy._format_expected(minimal=minimal + len(self._actions))

        def will_once(self, action):
            self._actions.append(action)
            self._expected_count = self._expected_count.adjust_by(1)
            return self

        def will_repeatedly(self, action):
            self._next_proxy = tmp = Expectation._RepeatedActionProxy(action, self._expectation)
            return tmp

    class _RepeatedActionProxy(_ProxyBase):

        def __init__(self, action, expectation):
            self._action = action
            self._expectation = expectation
            self._expected_count = None
            self._actual_count = 0
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
            return self._expected_count is None or\
                self._expected_count.is_satisfied(self._actual_count)

        def _format_action(self):
            return str(self._action)

        def _format_expected(self, minimal=None):
            minimal = minimal or 0
            if self._next_proxy is None:
                if self._expected_count is not None:
                    return self._expected_count.adjust_by(minimal).format_expected()
                elif minimal > 0:
                    return AtLeast(minimal).format_expected()
            elif self._expected_count is not None:
                return self._next_proxy._format_expected(
                    minimal=minimal + self._expected_count.minimal)

        def times(self, expected_count):
            self._expected_count = _wrap_expected_count(expected_count)
            return self

        def will_once(self, action):
            self._next_proxy = tmp = Expectation._ActionProxy(action, self._expectation)
            return tmp

        def will_repeatedly(self, action):
            self._next_proxy = tmp = self.__class__(action, self._expectation)
            return self

    def __init__(self, expected_call, filename, lineno):
        self._expected_call = expected_call
        self._filename = filename
        self._lineno = lineno
        self._next_proxy = self._DefaultProxy(self)
        self._total_calls = 0

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
        if not self.match(call):
            raise TypeError("expectation can only be called with matching 'Call' object")
        self._total_calls += 1
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

    def format_actual(self):
        """Return textual representation of how many times this expectation was
        called so far.

        This is used by :class:`mockify.exc.Unsatisfied` exception when
        rendering error message.
        """
        return _utils.format_actual_call_count(self._total_calls)

    def format_expected(self):
        """Return textual representation of how many times this expectation is
        expected to be called.

        This is used by :class:`mockify.exc.Unsatisfied` exception when
        rendering error message.
        """
        return self._next_proxy._format_expected()

    def format_action(self):
        """Return textual representation of next action to be executed.

        This method uses action's ``__str__`` method to render action name.

        Returns ``None`` if there were no actions recorded or all were
        consumed.

        This is used by :class:`mockify.exc.Unsatisfied` exception when
        rendering error message.
        """
        if hasattr(self._next_proxy, '_format_action'):
            return self._next_proxy._format_action()

    def format_location(self):
        """Return textual representation of place (filename and lineno) where
        this expectation was created.

        Basically, it just returns ``[filename]:[lineno]`` string, where
        ``filename`` and ``lineno`` are given via :class:`Expectation`
        constructor.
        """
        return "{}:{}".format(self._filename, self._lineno)

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
