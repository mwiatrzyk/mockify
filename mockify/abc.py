# ---------------------------------------------------------------------------
# mockify/abc.py
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
    """An interface to be implemented by classes used to obtain call location
    (file name and line number) from the stack.

    This is used when instance of :class:`ICall` is created to find a place in
    the code, where particular call object was created.

    Instances of :class:`ICallLocation` can be checked for (in)equality. Two
    call location objects are equal if and only if:

    * :attr:`filename` in both objects is the same
    * and :attr:`lineno` in both objects is the same
    """

    def __eq__(self, other: 'ICallLocation') -> bool:
        return isinstance(other, ICallLocation) and\
            self.filename == other.filename and\
            self.lineno == other.lineno

    def __ne__(self, other: 'ICallLocation') -> bool:
        return not self.__eq__(other)

    @property
    @abc.abstractmethod
    def filename(self) -> str:
        """File name."""

    @property
    @abc.abstractmethod
    def lineno(self) -> int:
        """Line number (within file given by :attr:`filename`)."""


class ICall(abc.ABC):
    """An interface to be implemented by objects containing mock call
    information.

    This information include:

    * full name of the mock
    * positional and keyword arguments the mock was called or is expected to be
      called with
    * location in user's code under test that created this mock object

    Call objects are created by mocks when mock receives a call from code being
    under test (so called **actual call**), or when expectation is recorded on
    a mock (so called **expected call**). Since call objects can be tested for
    (in)equality, Mockify internals can easily decide if expectation was met or
    not.
    """

    def __eq__(self, other: 'ICall') -> bool:
        return isinstance(other, ICall) and\
            self.name == other.name and\
            self.args == other.args and\
            self.kwargs == other.kwargs

    def __ne__(self, other: 'ICall') -> bool:
        return not self.__eq__(other)

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Full name of a mock for which this object was created."""

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
        def times(self, value: typing.Union[int, IExpectedCallCount]):
            """Used to configure how many times repeated action is expected to
            be called by a mock.

            See :meth:`IExpectation.times` for more details.
            """

    class IWillOnceMutation(abc.ABC):
        """Provides return value annotation and interface for **will_once()**
        methods."""

        @abc.abstractmethod
        def will_once(
            self, action: IAction
        ) -> 'IExpectation.IWillOnceMutation':
            """Attach next action to the end of action chain of current
            expectation object.

            See :meth:`IExpectation.will_once` for more details.
            """

        @abc.abstractmethod
        def will_repeatedly(
            self, action: IAction
        ) -> 'IExpectation.IWillRepeatedlyMutation':
            """Finalize action chain with a repeated action.

            See :meth:`IExpectation.will_repeatedly` for more details.
            """

    @abc.abstractmethod
    def times(self, value: typing.Union[int, IExpectedCallCount]):
        """Set expected call count of this expectation object.

        Following values are possible:

        * when :class:`int` parameter is used as a value, then expectation is
          expected to be called exactly *value* times,
        * when :class:`IExpectedCallCount` object is used as a value, then
          number of allowed expected calls depends on particular object that was
          used as a *value* (whether it was minimal, maximal or a range of
          expected call counts)

        See :ref:`setting-expected-call-count` tutorial section for more
        details.

        :param value:
            Expected call count value.

            This can be either a positive integer number (for a fixed expected
            call count), or an instance of :class:`IExpectedCallCount` class
            (for a more sophisticated expected call counts, like ranges etc.)
        """

    @abc.abstractmethod
    def will_once(self, action: IAction) -> IWillOnceMutation:
        """Attach next one-shot action to the end of the action chain of this
        expectation.

        When expectation is consumed, actions are consumed as well. If
        expectation is consumed for the first time, then first action is
        called. If it is consumed for the second time, then second action is
        consumed and so on. If there are no more actions and mock is called
        again, then :exc:`mockify.exc.OversaturatedCall` exception is raised.

        See :ref:`recording-action-chains` for more details about **action
        chains**.

        :param action:
            Action to be performed
        """

    @abc.abstractmethod
    def will_repeatedly(self, action: IAction) -> IWillRepeatedlyMutation:
        """Finalize action chain with a **repeated action**.

        Repeated actions can by default be invoked indefinitely by mock,
        unless expected call count is set explicitly with
        :meth:`IExpectation.IWillRepeatedlyMutation.times` method on a
        returned object. This is also a good way to set mock's default
        action.

        Since repeated actions act in a different way than one-time
        actions, there is currently not possible to record one-time actions
        after repeated action is set.

        See :ref:`recording-repeated-actions` for more details about **repeated
        actions**.

        :param action:
            Action to be performed
        """

    @abc.abstractmethod
    def is_satisfied(self) -> bool:
        """Check if this expectation object is **satisfied**.

        Expectations are satisfied if and only if:

        * all recorded one-shot actions were consumed
        * number of calls being made is within expected call count range

        This method is used by Mockify's internals to collect all unsatisfied
        expectations and raise :exc:`mockify.exc.Unsatisfied` exception.
        """


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
    mock object with methods, Mockify is first creating a "root" mock
    representing object, and then supplies it with child nodes, each pointing to
    "root" as a parent, and each representing single mocked method of that
    object.
    """

    @property
    def __m_fullname__(self) -> str:
        """Full name of this mock.

        This is calculated by prefixing :attr:`__m_name__` of this mock with a
        :attr:`__m_fullname__` property of this mock's parent, using ``.`` as a
        separator.

        If this mock has no parent, or parent does not have a name assigned,
        then this will be the same as :attr:`__m_name__`.
        """
        return self.__m_fullname_impl

    @_utils.memoized_property
    def __m_fullname_impl(self):
        parent = self.__m_parent__
        if parent is None or parent.__m_fullname__ is None:
            return self.__m_name__
        return "{}.{}".format(parent.__m_fullname__, self.__m_name__)

    def __m_walk__(self) -> typing.Iterator['IMock']:
        """Recursively iterate over mock subtree, from root to leafs, using
        *self* as a root.

        This method does that by recursively iterating over
        :meth:`__m_children__` iterator.

        It always yields *self* as first element.
        """

        def walk(mock):
            yield mock
            for child in mock.__m_children__():
                yield from walk(child)

        yield from walk(self)

    @property
    @abc.abstractmethod
    def __m_name__(self) -> str:
        """Name of this mock.

        Mock names are used for error reporting, to precisely point to mock and
        method that caused error. For root mocks you will have to provide names
        manually, and for leaf mocks the names will be picked automatically,
        using name of a method that is being mocked.

        This MUST BE a valid Python identifier, or a sequence of valid Python
        identifiers concatenated with a single ``.`` character.

        For example, valid names are::

            foo
            bar
            foobar123
            _foo_bar_123
            foo.bar.baz
        """

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
        """A reference to :class:`IMock` object that is a parent of this mock.

        If mock has no parent (i.e. if it's a root mock), then this should
        return ``None``.
        """

    @abc.abstractmethod
    def __m_expectations__(self) -> typing.Iterator[IExpectation]:
        """An iterator over :class:`IExpectation` objects recorded for
        this mock.

        This SHOULD NOT include expectations recorded for children of this mock.
        """

    @abc.abstractmethod
    def __m_children__(self) -> typing.Iterator['IMock']:
        """An iterator over :class:`IMock` objects representing direct
        children of this mock.

        This SHOULD NOT include grandchildren.
        """
