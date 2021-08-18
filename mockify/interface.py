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
import collections
import typing


class MockAttr:
    """Mock attribute wrapper/factory class.

    This is used to generate names of nested mocks out of identifier names when
    recording expectations with new functional API provided by
    :mod:`mockify.expect`. Instances of this class are returned by
    :class:`IMock` when you get attributes via class object, f.e:

    .. doctest::

        >>> IMock.foo.bar
        <MockAttr('foo.bar')>

    .. note::

        To avoid conflicts with Python's internals it is not possible to
        generate mock name by getting private attributes in a way presented
        above. Instead, you have to create :class:`MockAttr` instance
        explicitly, passing name (or path) as a string:

        .. doctest::

            >>> MockAttr('foo.bar._private')
            <MockAttr('foo.bar._private')>
    """

    def __init__(self, name: str, parent: 'MockAttr' = None):
        self._name = name
        self._parent = parent

    def __repr__(self):
        return "<{self.__class__.__qualname__}({path!r})>".format(
            self=self, path='.'.join(self.path())
        )

    def __getattr__(self, name: str) -> 'MockAttr':
        """Create and return new :class:`MockAttr` instance with given name and
        *self* as parent, effectively making a path to a nested mock
        attribute."""
        if not name.startswith('_'):
            return self.__class__(name, parent=self)
        else:
            raise AttributeError(name)

    def path(self) -> typing.Iterator[str]:
        """Return iterator over mock's attribute path components.

        An attrbute path is created when using identifier-based API, where one
        attribute is a parent for another:

        .. doctest::

            >>> attr = IMock.foo.bar.baz
            >>> list(attr.path())
            ['foo', 'bar', 'baz']

        Or explicitly, when path is given via :class:`MockAttr` constructor:

        .. doctest::

            >>> attr = MockAttr('foo.bar._private')
            >>> list(attr.path())
            ['foo', 'bar', '_private']

        """
        names = collections.deque(self._name.split('.'))
        current = self
        while current._parent is not None:
            current = current._parent
            names.appendleft(current._name)
        yield from names


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

    This can be either actual call (made by production code being under test),
    or an expected call (made by user in tests).
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


class _IMockMeta(abc.ABCMeta):

    def __getattr__(cls, name: str) -> MockAttr:
        if not name.startswith('_'):
            return MockAttr(name)
        else:
            raise AttributeError(name)


class IMock(abc.ABC, metaclass=_IMockMeta):
    """An interface to be implemented by all mock classes."""
