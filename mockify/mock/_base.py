# ---------------------------------------------------------------------------
# mockify/mock/_base.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import abc

from .. import _utils
from .._engine import Session


class BaseMock(abc.ABC):
    """Abstract base class for all mock classes.

    In Mockify, mocks are composed in a tree-like structure. For example, to
    mock object with a methods we compose object mock (a root) and then
    supply it with leafs (or children), each representing single mocked
    method of that object. This class provides methods and properties for
    Mockify engine to walk through such defined structure.

    If you need to declare your own mocks, make sure you implement this
    interface.

    :param name:
        Mock name.

        This is used for error reporting to display which mock has failed.
        This attribute must be set by inheriting class.

    :param session:
        Instance of :class:`mockify.Session` to be used.

        If not given, parent's session will be used if parent is set.
        Otherwise, a new session will be created.

    :param parent:
        Instance of :class:`BaseMock` representing parent for this mock.

        When this parameter is given, mock implicitly uses same session as
        given parent and uses parent's :attr:`__m_fullname__` as a prefix for
        its fullname.

    .. note::
        Parameters ``session`` and ``parent`` are self-exclusive and cannot
        be used simultaneously.

    .. versionchanged:: 0.9
        Added ``__init__`` method, as it is basically same for all mock
        classes.

    .. versionadded:: 0.8
    """

    def __init__(self, name=None, session=None, parent=None):
        self.__name = name
        self.__parent = _utils.make_weak(parent)
        if name is not None:
            _utils.validate_mock_name(name)
        if session is not None and parent is not None:
            raise TypeError("cannot set both 'session' and 'parent'")
        elif session is not None:
            self.__session = session
        elif parent is not None:
            self.__session = parent.__m_session__
        else:
            self.__session = Session()

    def __repr__(self):
        return "<{self.__module__}.{self.__class__.__name__}({self.__m_name__!r})>".format(self=self)

    @property
    def __m_name__(self) -> str:
        """Name of this mock."""
        return self.__name

    @property
    def __m_session__(self) -> Session:
        """Instance of :class:`mockify.Session` used by this mock.

        This should always be the same object for mock and all its children.
        """
        return self.__session

    @property
    def __m_parent__(self):
        """Weak reference to :class:`BaseMock` that is a parent of this
        mock.

        If mock has no parent, this should be set to ``None``.

        .. note::
            Make sure this property is always set in subclass to either
            parent object or ``None`` - otherwise you may get errors.
        """
        if self.__parent is not None:
            return self.__parent()

    @property
    def __m_fullname__(self):
        """Full name of this mock.

        It is composed of parent's :attr:`__m_fullname__` and current
        :attr:`__m_name__`. If mock has no parent, then this will be same as
        :attr:`__m_name__`.
        """
        parent = self.__m_parent__
        if parent is None or parent.__m_fullname__ is None:
            return self.__m_name__
        else:
            return "{}.{}".format(parent.__m_fullname__, self.__m_name__)

    def __m_walk__(self):
        """Recursively iterate over :class:`BaseMock` object yielded by
        :meth:`__m_children__` method.

        It always yields *self* as first element.

        This method is used by Mockify internals to collect all expectations
        recorded for mock and all its children.
        """

        def walk(mock):
            yield mock
            for child in mock.__m_children__():
                yield from walk(child)

        yield from walk(self)

    @abc.abstractmethod
    def __m_expectations__(self):
        """Iterator over :class:`mockify.Expectation` objects recorded for
        this mock.

        It should not include expectations recorded on mock's children. To
        get all expectations (including children), use :meth:`__m_walk__`.
        """

    @abc.abstractmethod
    def __m_children__(self):
        """Iterator over :class:`BaseMock` objects representing direct
        children of this mock.

        This should not include grandchildren.
        """


class MockInfo:
    """A class for inspecting mocks.

    This class simplifies access to mock's special properties and methods
    defined in :class:`BaseMock`, but wraps results (when applicable) with
    :class:`MockInfo` instances. If you need to access mock metadata in your
    tests, then this class is a recommended way to do this.

    :param target:
        Instance of :class:`BaseMock` object to be inspected
    """

    def __init__(self, target):
        if not isinstance(target, BaseMock):
            raise TypeError("__init__() got an invalid value for argument 'target'")
        self._target = target

    def __repr__(self):
        return "<{self.__module__}.{self.__class__.__name__}: {self._target!r}>".format(self=self)

    @property
    def mock(self):
        """Target mock that is being inspected.

        .. deprecated:: 0.8
            This is deprecated since version 0.8 and will be dropped in one
            of upcoming releases. Use :attr:`target` instead.
        """
        return self._target

    @property
    def target(self):
        """Reference to :class:`BaseMock` being inspected.

        .. versionadded:: 0.8
        """
        return self._target

    @property
    def parent(self):
        """A proxy to access :attr:`BaseMock.__m_parent__`.

        Returns ``None`` if target has no parent, or parent wrapped with
        :class:`MockInfo` object otherwise.

        .. versionadded:: 0.8
        """
        return self._target.__m_parent__

    @property
    def name(self):
        """A proxy to access :attr:`BaseMock.__m_name__` of target mock.

        .. versionchanged:: 0.8
            It is no longer full name; for that purpose use new :attr:`fullname`
        """
        return self._target.__m_name__

    @property
    def fullname(self):
        """A proxy to access :attr:`BaseMock.__m_fullname__` of target mock.

        .. versionadded:: 0.8
        """
        return self._target.__m_fullname__

    @property
    def session(self):
        """A proxy to access :attr:`BaseMock.__m_session__` of target mock."""
        return self._target.__m_session__

    def expectations(self):
        """An iterator over results returned by :meth:`BaseMock.__m_expectations__` method."""
        for expectation in self._target.__m_expectations__():
            yield expectation

    def children(self):
        """An iterator over results returned by :meth:`BaseMock.__m_children__` method.

        It wraps each found child with a :class:`MockInfo` object.
        """
        for child in self._target.__m_children__():
            yield self.__class__(child)

    def walk(self):
        """An iterator over results returnend by :meth:`BaseMock.__m_walk__` method.

        It wraps each found child with a :class:`MockInfo` object.
        """
        for child in self._target.__m_walk__():
            yield self.__class__(child)
