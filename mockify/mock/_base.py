# ---------------------------------------------------------------------------
# mockify/core/_base_mock.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

# pylint: disable=missing-module-docstring

from mockify import _utils
from mockify.abc import IMock, ISession
from mockify.core import Session

__all__ = export = _utils.ExportList()


@export
class BaseMock(IMock):  # pylint: disable=too-few-public-methods
    """Base class for all mock classes.

    This class provides partial implementation of :class:`mockify.abc.IMock`
    interface and common constructor used by all mocks. If you need to create
    custom mock, then it is better to inherit from this class at first place, as
    it provides some basic initialization out of the box.

    :param name:
        Name of this mock.

        This will be returned by :attr:`__m_name__` property.

        See :attr:`mockify.abc.IMock.__m_name__` for more information about
        naming mocks.

    :param session:
        Instance of :class:`mockify.abc.ISession` to be used.

        If not given, parent's session will be used (if parent exist) or a
        default :class:`mockify.core.Session` session object will be created and
        used.

        .. note::
            This option is self-exclusive with *parent* parameter.

    :param parent:
        Instance of :class:`mockify.abc.IMock` representing parent for this
        mock.

        When this parameter is given, mock implicitly uses paren't session
        object.

        .. note::
            This option is self-exclusive with *session* parameter.

    .. versionchanged:: (unreleased)
        Moved from :mod:`mockify.core` into :mod:`mockify.mock`.

    .. versionchanged:: 0.9
        Added ``__init__`` method, as it is basically same for all mock
        classes.

    .. versionadded:: 0.8
    """

    def __init__(self, name: str, session: ISession=None, parent: IMock=None):
        self.__name = name
        self.__parent = _utils.make_weak(parent)
        if name is not None:
            _utils.validate_mock_name(name)
        if session is not None and parent is not None:
            raise TypeError("cannot set both 'session' and 'parent'")
        if session is not None:
            self.__session = session
        elif parent is not None:
            self.__session = parent.__m_session__
        else:
            self.__session = Session()

    def __repr__(self):
        return "<{self.__module__}.{self.__class__.__qualname__}({self.__m_name__!r})>".format(
            self=self
        )

    @property
    def __m_name__(self) -> str:
        """See :meth:`mockify.abc.IMock.__m_name__`."""
        return self.__name

    @property
    def __m_session__(self) -> ISession:
        """See :meth:`mockify.abc.IMock.__m_session__`."""
        return self.__session

    @property
    def __m_parent__(self) -> IMock:
        """See :meth:`mockify.abc.IMock.__m_parent__`."""
        if self.__parent is not None:
            return self.__parent()
        return None


@export
class MockInfo:
    """A class for inspecting mocks.

    This class simplifies and extends access to mock's special properties and
    methods defined in :class:`BaseMock`, but wraps results (when applicable)
    with :class:`MockInfo` instances. If you need to access mock metadata in
    your tests, or when you build your own mocks from the scratch, then you
    should use this class.

    :param target:
        Instance of :class:`BaseMock` object to be inspected

    .. deprecated:: (unreleased)
        This class is obsolete and will be removed in one of upcoming releases.
        Entire functionality is currently provided by Mockify-defined special
        methods in :class:`mockify.abc.IMock` class.
    """

    def __init__(self, target: BaseMock):
        if not isinstance(target, BaseMock):
            raise TypeError(
                "__init__() got an invalid value for argument 'target'"
            )
        self._target = target

    def __repr__(self):
        return "<mockify.mock.{self.__class__.__qualname__}: {self._target!r}>".format(
            self=self
        )

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
        parent = self._target.__m_parent__
        if parent is None:
            return None
        return self.__class__(parent)

    @property
    def name(self):
        """A proxy to access :attr:`BaseMock.__m_name__` of target mock.

        .. versionchanged:: 0.8
            It is no longer full name; for that purpose use new :attr:`fullname`
        """
        return self._target.__m_name__

    @property
    def fullname(self):
        """Return full name of underlying mock.

        Mock's full name is calculated by concatenating :attr:`fullname` of
        info object representing mock's parent, with :attr:`name` of this
        info object. If there is no parent or parent has no full name, then
        this is the same as :attr:`name`.

        .. versionadded:: 0.8
        """
        parent = self.parent
        if parent is None or parent.fullname is None:
            return self.name
        return "{}.{}".format(parent.fullname, self.name)

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
        """Recursively iterate over :class:`MockInfo` instances yielded by
        :meth:`children` generator.

        It always yields *self* as first element.

        This method is used by Mockify internals to collect all expectations
        recorded for mock and all its children.
        """

        def walk(mock):
            yield mock
            for child in mock.children():
                yield from walk(child)

        yield from walk(self)
