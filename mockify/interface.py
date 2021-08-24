# ---------------------------------------------------------------------------
# mockify/interface.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
"""ABC classes for Mockify."""

import abc
import typing

from . import _utils


class ICallLocation(abc.ABC):
    """Points to the place in user's source code where some :class:`ICall`
    object was created.

    This can point to either place in production code, where mock call was
    made, or to a place in test code, where particular expectation (i.e.
    *expected* call) was recorded.
    """

    @property
    @abc.abstractmethod
    def filename(self) -> str:
        """File name."""

    @property
    @abc.abstractmethod
    def lineno(self) -> int:
        """Line number (within file given by :attr:`filename`)."""


class ICall(abc.ABC):
    """Contains mock call information.

    This can be either actual call (it then points to a location in production
    code where mock was called), or an expected call (it then points to test
    file where expectation was created).
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Full name of a mock that call was made on."""

    @property
    @abc.abstractmethod
    def args(self) -> typing.Tuple[typing.Any]:
        """Positional args passed to the call object during creation."""

    @property
    @abc.abstractmethod
    def kwargs(self) -> typing.Dict[str, typing.Any]:
        """Named args passed to the call object during creation."""

    @property
    @abc.abstractmethod
    def location(self) -> ICallLocation:
        """A place in user's source code where this call object was created."""


class IAction(abc.ABC):
    """An interface to be implemented by mock actions.

    Actions are registered on mocks with a help of
    :meth:`IExpectation.will_once` and :meth:`IExpectation.will_repeatedly`
    methods and are used to set what the mock must do once called by code being
    under test. The most trivial action is to set a mock return value, or force
    it to raise given exception. Please proceed to :mod:`mockify.actions` to
    get familiar with a bulk of built-in implementations.
    """

    @abc.abstractmethod
    def __call__(self, actual_call: ICall) -> typing.Optional[typing.Any]:
        """Action body.

        This is the place where actual action execution takes place.

        :param actual_call:
            Mock call params wrapped with :class:`ICall` object.

            Use this to get access to parameters passed to mock when it was
            called by code being under test.
        """


class IExpectedCallCount(abc.ABC):
    """An interface to be implemented by classes that set expected call count
    ranges.

    Instances of this class are used by :meth:`IExpectation.times` and
    :meth:`IExpectation.IWillRepeatedlyMutation.times` methods to set how many
    times the mock is expected to be called. You can find built-in
    implementations of this interface in :mod:`mockify.cardinality` module.
    """

    @abc.abstractmethod
    def match(self, actual_call_count: int) -> bool:
        """Check if actual number of calls matches expected number of calls."""


class IExpectation(abc.ABC):
    """Represents single expectation recorded on a mock.

    Instances of this class are created by mock's **expect_call()** method or
    by using functions from :mod:`mockify.expect` module.
    """

    class IWillRepeatedlyMutation(abc.ABC):
        """Provides return value annotation and interface for
        **will_repeatedly()** methods."""

        @abc.abstractmethod
        def times(
            self, cardinality: IExpectedCallCount
        ):
            """Used to configure how many times repeated action is expected to
            be called by mock."""

    class IWillOnceMutation(abc.ABC):
        """Provides return value annotation and interface for **will_once()**
        methods."""

        @abc.abstractmethod
        def will_once(
            self, action: IAction
        ) -> 'IExpectation.IWillOnceMutation':
            """Attach next one-time action to the action chain of current
            expectation."""

        @abc.abstractmethod
        def will_repeatedly(
            self, action: IAction
        ) -> 'IExpectation.IWillRepeatedlyMutation':
            """Finalize action chain with a repeated action.

            Repeated actions can by default be invoked indefinitely by mock,
            unless expected call count is set explicitly with
            :meth:`IExpectation.IWillRepeatedlyMutation.times` method on a
            returned object. This is also a good way to set mock's default
            action.

            Since repeated actions act in a different way than one-time
            actions, there is currently not possible to record one-time actions
            after repeated action is set.
            """

    @abc.abstractmethod
    def times(self, value: typing.Union[int, IExpectedCallCount]):
        """Set expected call count of this expectation object.

        :param value:
            Expected call count value.

            This can be either a positive integer number (for a fixed expected
            call count), or an instance of :class:`IExpectedCallCount` class
            (for a more sophisticated expected call counts, like ranges etc.)
        """

    @abc.abstractmethod
    def will_once(self, action: IAction) -> IWillOnceMutation:
        """See :meth:`IExpectation.IWillOnceMutation.will_once`."""

    @abc.abstractmethod
    def will_repeatedly(self, action: IAction) -> IWillRepeatedlyMutation:
        """See :meth:`IExpectation.IWillOnceMutation.will_repeatedly`."""


class ISession(abc.ABC):
    """An interface to be implemented by session classes.

    In Mockify, sessions are used to keep track of recorded and consumed
    expectations of each mock sharing one session object. Every created
    :class:`IExpectation` object is stored in the session attached to a mock
    being used and every call made to that mock is reported in that session.
    Thanks to this, Mockify can tell (at the end of each test) which
    expectations were consumed, and which were not.
    """


class IMock(abc.ABC):
    """An interface to be implemented by mock classes.

    In Mockify, mocks are organized in a tree-like structure. For example, to
    mock object with a methods we compose a root mock representing object and
    then supply it with leafs (or children), each representing single mocked
    method of that object.
    """

    @property
    def __m_fullname__(self) -> str:
        """Full name of this mock.

        Full mock names are calculated using this mock's parent's
        :attr:`__m_fullname__`, and this mock's :attr:`__m_name__` value by
        concatenating both with a period sign.

        If this mock has no parent, or this mock's parent does not have a name,
        then this will be the same as :attr:`__m_name__`.

        Full mock names are unique across session this mock belongs to.
        """
        return self.__m_fullname_impl

    @_utils.memoized_property
    def __m_fullname_impl(self):
        parent = self.__m_parent__
        if parent is None or parent.__m_fullname__ is None:
            return self.__m_name__
        return "{}.{}".format(parent.__m_fullname__, self.__m_name__)

    @property
    @abc.abstractmethod
    def __m_name__(self) -> str:
        """Name of this mock."""

    @property
    @abc.abstractmethod
    def __m_session__(self) -> ISession:
        """Instance of :class:`ISession` to be used by this mock.

        Value returned by this property MUST meet following condition::

            if self.__m_parent__ is not None:
                assert self.__m_session__ is self.__m_parent__.__m_session__

        In other words, if this mock has a parent, than it MUST be attached to
        same session object as its parent.
        """

    @property
    @abc.abstractmethod
    def __m_parent__(self) -> typing.Optional['IMock']:
        """A weak reference to :class:`IMock` object being a parent for this
        mock.

        If mock has no parent (i.e. if it's a root mock), then this should
        return ``None``.
        """

    @abc.abstractmethod
    def __m_expectations__(self) -> typing.Iterator[IExpectation]:
        """An iterator over :class:`IExpectation` objects recorded for
        this mock.

        This SHOULD NOT include expectations recorded on this mock's children
        (if any).
        """

    @abc.abstractmethod
    def __m_children__(self) -> typing.Iterator['IMock']:
        """An iterator over :class:`IMock` objects representing direct
        children of this mock.

        This SHOULD NOT include grandchildren.
        """
