# ---------------------------------------------------------------------------
# mockify/_engine.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import os
import keyword
import weakref
import warnings
import itertools
import traceback
import collections

from contextlib import contextmanager

from . import exc, _utils
from .cardinality import Exactly, AtLeast

__all__ = export = _utils.ExportList()

_mockify_root_dir = os.path.dirname(__file__)


def _wrap_expected_count(expected_count):
    if isinstance(expected_count, int):
        return Exactly(expected_count)
    else:
        return expected_count


class _ExpectationFilter:

    def __init__(self, expectations):
        self._expectations = expectations

    def __iter__(self):
        return iter(self._expectations)

    def by_call(self, call):
        return self.__class__(
            filter(lambda x: x.expected_call == call, self._expectations))

    def by_name(self, name):
        return self.__class__(
            filter(lambda x: x.expected_call.name == name, self._expectations))

    def unsatisfied(self):
        return self.__class__(
            filter(lambda x: not x.is_satisfied(), self._expectations))


@export
@contextmanager
def ordered(*mocks):
    """Preserve order in what expectations are defined.

    Use this to wrap test fragment in which you are recording expectations.
    All expectations recorded for listed mocks will be tracked and their
    order will be strictly checked during unit under test execution. If one
    expectation is called earlier than another, then execution will fail with
    an error.
    """

    def get_context():
        num_mocks = len(mocks)
        if num_mocks == 1:
            return MockInfo(mocks[0]).ctx
        for i in range(num_mocks-1):
            first, second = MockInfo(mocks[i]), MockInfo(mocks[i+1])
            ctx = first.ctx
            if ctx is not second.ctx:
                raise TypeError(
                    f"Unable to use ordered expectations: "
                    f"mocks {mocks[i]!r} and {mocks[i+1]!r} use different "
                    f"contexts.")
        else:
            return ctx

    ctx = get_context()
    ctx.enable_ordered(*map(lambda x: MockInfo(x).name, mocks))
    yield
    ctx.disable_ordered()


@export
@contextmanager
def satisfies(*mocks):
    """Context manager for checking if given mocks are all satisfied when
    leaving the scope.

    It can be used with any mock and also with :class:`mockify.Registry`
    instances. The purpose of using this context manager is to emphasize the
    place in test code where given mocks are used.

    Here's an example test:

    .. testcode::

        from _mockify.mock import Function
        from _mockify.actions import Return

        class MockCaller:

            def __init__(self, mock):
                self._mock = mock

            def call_mock(self, a, b):
                return self._mock(a, b)

        def test_mock_caller():
            mock = Function('mock')

            mock.expect_call(1, 2).will_once(Return(3))

            uut = MockCaller(mock)
            with assert_satisfied(mock):
                assert uut.call_mock(1, 2) == 3

    .. testcleanup::

        test_mock_caller()
    """
    yield
    unsatisfied_expectations = itertools.chain(*map(lambda x: MockInfo(x).unsatisfied_expectations, mocks))
    unsatisfied_expectations = list(unsatisfied_expectations)
    if unsatisfied_expectations:
        raise exc.Unsatisfied(unsatisfied_expectations)


@export
@contextmanager
def assert_satisfied(*mocks):
    """Context manager for ensuring that all given mocks are satisfied when
    leaving the scope.

    .. deprecated:: 0.6
        This function was renamed to :func:`satisfies` and will be removed in
        one of upcoming releases.
    """
    with satisfies(*mocks):
        yield


@export
class MockInfo:

    def __init__(self, mock):
        self._mock = mock

    @property
    def ctx(self):
        return self._mock._ctx

    @property
    def name(self):
        return self._mock._name

    @property
    def unsatisfied_expectations(self):
        return self._mock._ctx._expectations.by_name(self.name).unsatisfied()


@export
class Call:
    """An object representing mock call.

    Instances of this class are created when expectations are recorded or
    when mock is called. The role of this class is to keep mock name and its
    call params as a single object for easier comparison between expected and
    actual mock calls.

    This class also provides some basic stack info to be used for error
    reporting (f.e. to display where failed expectation was defined).
    """

    def __init__(self, *args, **kwargs):
        if not args:
            raise TypeError("__init__() missing 1 required positional argument: 'name'")
        self._name = args[0]
        self._args = args[1:]
        self._kwargs = kwargs
        self._location = self.__extract_fileinfo_from_traceback()
        self.__validate_name()

    def __extract_fileinfo_from_traceback(self):
        stack = traceback.extract_stack()
        for frame in reversed(stack):
            if not frame.filename.startswith(_mockify_root_dir):
                return frame.filename, frame.lineno

    def __validate_name(self):
        parts = self._name.split('.') if isinstance(self._name, str) else [self._name]
        for part in parts:
            if not self.__is_identifier(part):
                raise exc.InvalidMockName(invalid_name=self._name)

    def __is_identifier(self, name):
        return isinstance(name, str) and\
            name.isidentifier() and\
            not keyword.iskeyword(name)

    def __str__(self):
        return f"{self._name}({self._format_params(*self._args, **self._kwargs)})"

    def __repr__(self):
        return f"<mockify.{self.__class__.__name__}({self._format_params(self._name, *self._args, **self._kwargs)})>"

    def __eq__(self, other):
        return self._name == other._name and\
            self._args == other._args and\
            self._kwargs == other._kwargs

    def __ne__(self, other):
        return not self.__eq__(other)

    def _format_params(self, *args, **kwargs):
        args_gen = (repr(x) for x in args)
        kwargs_gen = ("{}={!r}".format(k, v) for k, v in sorted(kwargs.items()))
        all_gen = itertools.chain(args_gen, kwargs_gen)
        return ', '.join(all_gen)

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

    @property
    def location(self):
        """Location (a tuple containing file name and line number) where this
        call object was created.

        .. versionadded:: 0.6

        This is used to display where failed expectation was declared or
        where failed call was orinally made.
        """
        return self._location


@export
class Context:
    _uninterested_call_strategies = ('fail', 'warn', 'ignore')

    def __init__(self, uninterested_call_strategy='fail'):
        self.__expectations = []
        self._ordered_expectations = collections.deque()
        self._ordered_expectations_enabled_for = set()
        self.uninterested_call_strategy = uninterested_call_strategy

    def __call__(self, actual_call):
        if self._is_ordered(actual_call):
            return self.__call_ordered(actual_call)
        else:
            return self.__call_unordered(actual_call)

    def __call_ordered(self, actual_call):
        head = self._ordered_expectations[0]
        if head.expected_call == actual_call:
            try:
                return head(actual_call)
            finally:
                if head.is_satisfied():
                    self._ordered_expectations.popleft()
        else:
            raise exc.UnexpectedCallOrder(actual_call, head.expected_call)

    def __call_unordered(self, actual_call):
        found_by_call = list(self._expectations.by_call(actual_call))
        if not found_by_call:
            return self.__handle_uninterested_call(actual_call)
        for expectation in found_by_call:
            if not expectation.is_satisfied():
                return expectation(actual_call)
        else:
            return found_by_call[-1](actual_call)  # Oversaturate last found if all are satisfied

    def __handle_uninterested_call(self, actual_call):
        if self.uninterested_call_strategy == 'fail':
            self.__handle_uninterested_call_using_fail_strategy(actual_call)
        elif self.uninterested_call_strategy == 'ignore':
            pass
        elif self.uninterested_call_strategy == 'warn':
            warnings.warn(str(actual_call), exc.UninterestedCallWarning)

    def __handle_uninterested_call_using_fail_strategy(self, actual_call):
        found_by_name = list(self._expectations.by_name(actual_call.name))
        if not found_by_name:
            raise exc.UninterestedCall(actual_call)
        else:
            raise exc.UnexpectedCall(actual_call, found_by_name)

    @property
    def _expectations(self):
        return _ExpectationFilter(self.__expectations)

    @property
    def uninterested_call_strategy(self):
        return self._uninterested_call_strategy

    @uninterested_call_strategy.setter
    def uninterested_call_strategy(self, value):
        if value not in self._uninterested_call_strategies:
            raise ValueError(f"invalid strategy given: {value}")
        self._uninterested_call_strategy = value

    def expect_call(self, expected_call):
        expectation = Expectation(expected_call)
        if self._is_ordered(expected_call):
            self._ordered_expectations.append(expectation)
        else:
            self.__expectations.append(expectation)
        return expectation

    def assert_satisfied(self):
        unsatisfied_expectations = list(self._expectations.unsatisfied())
        if unsatisfied_expectations:
            raise exc.Unsatisfied(unsatisfied_expectations)

    def enable_ordered(self, *names):
        self._ordered_expectations_enabled_for = set(names)
        self._ordered_expectations = collections.deque()

    def disable_ordered(self):
        self._ordered_expectations_enabled_for = set()

    def _is_ordered(self, call):
        for prefix in self._ordered_expectations_enabled_for:
            if call.name.startswith(prefix):
                return True
        return False


#@export
class Registry:
    """Groups unrelated mocks together and acts as a common database for
    recorded expectations.

    Objects of this class become a backend for all mocks that use it. While
    mocks are responsible to act in the same manner as object they imitate,
    such registry is responsible for receiving expectations and calls from
    that mocks.

    :param expectation_class:
        Provide :class:`Expectation` subclass to be used.

        Since this class creates expectations internally, this parameter will
        allow injecting another expectation class that will be used to
        represent all expectations within this registry.

    :param uninterested_call_strategy:
        Setup the way of how uninterested calls are treated.

        By default, when mock is called with no expectation set on it first,
        then :exc:`mockify.exc.UninterestedCall` is raised. Other
        possibilities are:

            * *ignore* - do nothing on uninterested calls
            * *warn* - issue warnings on uninterested calls

        This value is common for all mocks that share this registry.

        .. versionadded:: 0.4
    """

    def __init__(self,
            expectation_class=None,
            expectation_query_class=None,
            uninterested_call_strategy='fail'):
        self._expects = []
        self._expectation_class = expectation_class or Expectation
        self._expectation_query_class = expectation_query_class or ExpectationQuery
        self._uninterested_call_strategy = uninterested_call_strategy

    def register_mock(self, name):
        pass

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
        matching_expects = self.expectations.by_call(call).all()
        if not matching_expects:
            return self._handle_uninterested_call(call)
        for expect in matching_expects:
            if not expect.is_satisfied():
                return expect(call)
        else:
            return matching_expects[-1](call)

    def _handle_uninterested_call(self, call):
        if self._uninterested_call_strategy == 'fail':
            other_expectations = self.expectations.by_name(call.name).all()
            if other_expectations:
                raise exc.UnexpectedCall(call, other_expectations)
            else:
                raise exc.UninterestedCall(call)
        elif self._uninterested_call_strategy == 'warn':
            warnings.warn('Uninterested mock called: {}'.format(str(call)))
        elif self._uninterested_call_strategy == 'ignore':
            return
        else:
            raise ValueError("Invalid uninterested call strategy: {}".format(self._uninterested_call_strategy))

    @property
    def expectations(self):
        """Allows to filter out expectations using generic and easy to extend
        interface.

        .. versionadded:: 0.6

        This property returns instance of :class:`ExpectationQuery` class.
        """
        return self._expectation_query_class(self._expects)

    def expect_call(self, call, filename=None, lineno=None):
        """Register expectation.

        Returns instance of ``expectation_class`` (usually
        :class:`Expectation`) representing newly created expectation.

        :param call:
            Instance of :class:`mockify.engine.Call` class representing exact
            mock call or a pattern (if created with matchers) that is expected
            to be executed

        :param filename:
            Path to file were expectation is created

            .. deprecated:: 0.6
                This parameter is no longer used and will be removed in one
                of upcoming releases.

        :param lineno:
            Line number (inside ``filename``) where expectation is created

            .. deprecated:: 0.6
                This parameter is no longer used and will be removed in one
                of upcoming releases.
        """
        expect = self._expectation_class(call)
        self._expects.append(expect)
        return expect

    def assert_satisfied(self, *names):
        """Assert that all expectations are satisfied.

        If there is at least one unsatisfied expectation, then this method will
        raise :exc:`mockify.exc.Unsatisfied` exception containing list of
        failed expectations.

        This method can be called as many times as you want as it does not
        change internal state of registry.

        .. versionchanged:: 0.2
            Accepts names of mocks to check as positional args. If one or more
            names are given, then this method limits checking only to mocks of
            matching names.

        .. versionchanged:: 0.6
            Giving *names* is now deprecated.

            See :attr:`expectations` attribute for more details.
        """
        if names:
            warnings.warn("Using 'names' is deprecated since 0.6 - use 'expectations' attribute instead")
            self.expectations.by_any_name(names).assert_satisfied()
        else:
            self.expectations.all().assert_satisfied()


@export
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

    def __init__(self, expected_call, filename=None, lineno=None):
        self._expected_call = expected_call
        self._filename, self._lineno = expected_call.location
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
