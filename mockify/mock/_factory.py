# ---------------------------------------------------------------------------
# mockify/mock/_factory.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import weakref

from ._mock import Mock
from ._base import BaseMock
from .._engine import Session


class MockFactory(BaseMock):
    """A factory class used to create groups of related mocks.

    This class allows to create mocks using class given by *mock_class*
    ensuring that:

    * names of created mocks are **unique**,
    * all mocks share one common session object.

    Instances of this class keep track of created mocks. Moreover, functions
    that would accept :class:`Mock` instances will also accept
    :class:`MockFactory` instances, so you can later f.e. check if all
    created mocks are satisfied using just a factory object. That makes it
    easy to manage multiple mocks in large test suites.

    See :ref:`managing-multiple-mocks` for more details.

    .. versionchanged:: 0.8
        Now it inherits from :class:`mockify.mock.BaseMock`, as this class is
        more or less special kind of mock.

    .. versionadded:: 0.6

    :param name:
        This is optional.

        Name of this factory to be used as a common prefix for all created
        mocks and nested factories.

    :param session:
        Instance of :class:`mockify.Session` to be used.

        If not given, a default session will be created and shared across all
        mocks created by this factory.

    :param mock_class:
        The class that will be used by this factory to create mocks.

        By default it will use :class:`Mock` class.
    """

    def __init__(self, name=None, session=None, mock_class=None):
        self._name = name
        self._session = session or Session()
        self._mock_class = mock_class or Mock
        self._factories = {}
        self._mocks = {}
        self.__m_parent__ = None

    @property
    def __m_name__(self):
        return self._name

    @property
    def __m_fullname__(self):
        parent = self.__m_parent__
        if parent is None or parent.__m_fullname__ is None:
            return self.__m_name__
        else:
            return "{}.{}".format(parent.__m_fullname__, self.__m_name__)

    @property
    def __m_session__(self):
        return self._session

    @property
    def __m_parent__(self):
        if self.__parent is not None:
            return self.__parent()

    @__m_parent__.setter
    def __m_parent__(self, value):
        if value is None:
            self.__parent = value
        else:
            self.__parent = weakref.ref(value)

    def __m_children__(self):
        yield from self._mocks.values()
        yield from self._factories.values()

    def __m_expectations__(self):
        for mock in self._mocks.values():
            yield from mock.__m_expectations__()

    def __repr__(self):
        return "<{self.__module__}.{self.__class__.__name__}({self.__m_fullname__!r})>".format(self=self)

    def mock(self, name):
        """Create and return mock of given *name*.

        This method will raise :exc:`TypeError` if *name* is already used by
        either mock or child factory.
        """
        self._validate_name(name)
        self._mocks[name] = tmp =\
            self._mock_class(self.__format_name(name), session=self._session)
        return tmp

    def __format_name(self, name):
        if self.__m_fullname__ is None:
            return name
        else:
            return "{}.{}".format(self.__m_fullname__, name)

    def factory(self, name):
        """Create and return child factory.

        Child factory will use session from its parent, and will prefix all
        mocks and grandchild factories with given *name*.

        This method will raise :exc:`TypeError` if *name* is already used by
        either mock or child factory.

        :rtype: MockFactory
        """
        self._validate_name(name)
        self._factories[name] = tmp =\
            self.__class__(
                name=name,
                session=self._session,
                mock_class=self._mock_class)
        tmp.__m_parent__ = self
        return tmp

    def _validate_name(self, name):
        if name in self._mocks or name in self._factories:
            raise TypeError("Name {!r} is already in use".format(name))
