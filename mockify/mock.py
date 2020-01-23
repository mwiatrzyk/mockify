# ---------------------------------------------------------------------------
# mockify/mock.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import weakref
import itertools

from . import _utils
from ._engine import Call, Session
from .matchers import _


class _ChildMock:
    _mocked_properties = {
        '__getattr__': lambda: _GetAttrMock,
        '__setattr__': lambda: _SetAttrMock,
        'expect_call': lambda: _ExpectCallMock,
    }

    def __init__(self, name, session, parent):
        _utils.validate_mock_name(name)
        self._name = name
        self._session = session
        self._parent = parent

    def __repr__(self):
        return f"<{self.__module__}.{self.__class__.__name__}({self._fullname!r})>"

    def __setattr__(self, name, value):
        if '__setattr__' in self.__dict__:
            return self.__dict__['__setattr__'](name, value)
        else:
            return super().__setattr__(name, value)

    def __getattr__(self, name):
        if '__getattr__' in self.__dict__ :
            return self.__dict__['__getattr__'](name)
        else:
            self.__dict__[name] = tmp = _ChildMock(name, self._session, self)
            return tmp

    def __getattribute__(self, name):
        if name == '_mocked_properties':
            return super().__getattribute__(name)
        elif name not in self._mocked_properties:
            return super().__getattribute__(name)
        elif name in self.__dict__:
            return self.__dict__[name]
        else:
            mock_class = self._mocked_properties[name]()
            self.__dict__[name] = tmp = mock_class(self._session, self)
            return tmp

    def __call__(self, *args, **kwargs):
        actual_call = Call(self._fullname, *args, **kwargs)
        return self._session(actual_call)

    def expect_call(self, *args, **kwargs):
        expected_call = Call(self._fullname, *args, **kwargs)
        return self._session.expect_call(expected_call)

    @property
    def _parent(self):
        if self.__parent is not None:
            return self.__parent()

    @_parent.setter
    def _parent(self, value):
        if value is None:
            self.__parent = value
        else:
            self.__parent = weakref.ref(value)

    @property
    def _fullname(self):
        parent = self._parent
        if parent is None:
            return self._name
        else:
            return f"{parent._fullname}.{self._name}"

    @property
    def _children(self):
        for obj in self.__dict__.values():
            if isinstance(obj, _ChildMock):
                yield obj

    @property
    def _expectations(self):
        return filter(
            lambda x: x.expected_call.name == self._fullname,
            self._session.expectations)


class _GetAttrMock(_ChildMock):
    _mocked_properties = {}

    def __init__(self, session, parent):
        super().__init__('__getattr__', session, parent)

    def __call__(self, name):
        actual_call = Call(self._fullname, name)
        return self._session(actual_call)

    def expect_call(self, name):
        if not _utils.is_identifier(name):
            raise TypeError(f"__getattr__.expect_call() must be called with valid Python property name, got {name!r}")
        if name in self._parent.__dict__:
            raise TypeError(
                f"__getattr__.expect_call() must be called with a non existing property name, "
                f"got {name!r} which already exists")
        expected_call = Call(self._fullname, name)
        return self._session.expect_call(expected_call)


class _SetAttrMock(_ChildMock):
    _mocked_properties = {}

    def __init__(self, session, parent):
        super().__init__('__setattr__', session, parent)

    def __call__(self, name, value):
        actual_call = Call(self._fullname, name, value)
        return self._session(actual_call)

    def expect_call(self, name, value):
        if not _utils.is_identifier(name):
            raise TypeError(f"__setattr__.expect_call() must be called with valid Python property name, got {name!r}")
        if name in self._parent.__dict__:
            raise TypeError(
                f"__setattr__.expect_call() must be called with a non existing property name, "
                f"got {name!r} which already exists")
        expected_call = Call(self._fullname, name, value)
        return self._session.expect_call(expected_call)


class _ExpectCallMock(_ChildMock):

    def __init__(self, session, parent):
        super().__init__('expect_call', session, parent)

    def __call__(self, *args, **kwargs):
        query = _utils.IterableQuery(self._session.expectations)
        if query.exists(lambda x: x.expected_call.name == self._fullname):
            return self._call(*args, **kwargs)
        else:
            return self._expect_call(*args, **kwargs)

    def _call(self, *args, **kwargs):
        actual_call = Call(self._fullname, *args, **kwargs)
        return self._session(actual_call)

    def _expect_call(self, *args, **kwargs):
        expected_call = Call(self._parent._fullname, *args, **kwargs)
        return self._session.expect_call(expected_call)


class MockInfo:
    """Allows to read some metainformation from given *mock* object."""

    def __init__(self, mock):
        self._mock = mock

    @property
    def mock(self):
        """Reference to target mock object."""
        return self._mock

    @property
    def name(self):
        """Name of target mock."""
        return self._mock._fullname

    @property
    def expectations(self):
        """An iterator over all expectations recorded for target mock."""
        return self._mock._expectations

    @property
    def children(self):
        """An iterator over target mock's children."""
        return self._mock._children

    def walk(self):
        """Recursively iterate over all target mock's children (including
        target mock itself) in depth-first order and yield :class:`MockInfo`
        object for each found mock.
        """

        def walk(mock):
            yield self.__class__(mock)
            for child_mock in self.__class__(mock).children:
                yield from walk(child_mock)

        yield from walk(self._mock)


class MockFactory:
    """A factory class used to create groups of related mocks.

    This can be used if you need to create several mocks that need to be
    checked all at once.

    :param session:
        Instance of :class:`mockify.Session` to be used.
    """

    def __init__(self, session=None, mock_class=None):
        self._session = session or Session()
        self._mock_class = mock_class or Mock
        self._created_mocks = {}

    def __getattr__(self, name):
        if name not in self._created_mocks:
            self._created_mocks[name] = self._mock_class(name, session=self._session)
        return self._created_mocks[name]

    @property
    def _children(self):
        return iter(self._created_mocks.values())

    @property
    def _expectations(self):
        for mock in self._created_mocks.values():
            yield from mock._expectations


class Mock(_ChildMock):
    """General purpose mocking utility.

    This class can be used to mock functions, methods, getters & setters,
    modules and can also be used to create ad-hoc data objects. See
    :ref:`Tutorial` for more details.
    """

    def __init__(self, name, session=None):
        super().__init__(name, session or Session(), None)
