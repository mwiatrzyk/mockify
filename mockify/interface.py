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
    pass


class IExpectedCallCount(abc.ABC):
    pass


class IExpectation(abc.ABC):

    class ITimesMutation(abc.ABC):
        pass

    class IWillRepeatedlyMutation(abc.ABC):

        @abc.abstractmethod
        def times(
            self, cardinality: IExpectedCallCount
        ) -> 'IExpectation.ITimesMutation':
            pass

    class IWillOnceMutation(abc.ABC):

        @abc.abstractmethod
        def will_once(
            self, action: IAction
        ) -> 'IExpectation.IWillOnceMutation':
            pass

        @abc.abstractmethod
        def will_repeatedly(
            self, action: IAction
        ) -> 'IExpectation.IWillRepeatedlyMutation':
            pass

    @abc.abstractmethod
    def __call__(self, actual_call: ICall) -> typing.Optional[typing.Any]:
        pass

    @abc.abstractmethod
    def times(self, cardinality: IExpectedCallCount) -> ITimesMutation:
        pass

    @abc.abstractmethod
    def will_once(self, action: IAction) -> IWillOnceMutation:
        pass

    @abc.abstractmethod
    def will_repeatedly(self, action: IAction) -> IWillRepeatedlyMutation:
        pass


class _IMockMeta(abc.ABCMeta):

    def __getattr__(cls, name: str) -> MockAttr:
        if not name.startswith('_'):
            return MockAttr(name)
        else:
            raise AttributeError(name)


class IMock(abc.ABC, metaclass=_IMockMeta):
    pass
