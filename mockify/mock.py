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

_EXPECT_CALL_METHOD_NAME = 'expect_call'


class MockInfo:

    def __init__(self, mock):
        self._mock = mock

    @property
    def mock(self):
        return self._mock

    @property
    def name(self):
        return self._mock._fullname

    @property
    def expectations(self):
        return self._mock._expectations

    @property
    def children(self):
        return self._mock._children

    def walk(self):
        """This is used to recursively iterate over all mock objects that are
        part of target mock.

        This method yields instances of :class:`MockInfo` for each mock
        object it finds.
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


class BaseMock:

    def __init__(self, name, session, parent=None):
        self._name = name
        self._session = session
        self._parent = parent

    def __repr__(self):
        return f"<{self.__module__}.{self.__class__.__name__}({self._fullname!r})>"

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
            if isinstance(obj, BaseMock):
                if not obj._name == _EXPECT_CALL_METHOD_NAME:
                    yield obj

    @property
    def _expectations(self):
        return filter(
            lambda x: x.expected_call.name == self._fullname,
            self._session.expectations)


class Mock(BaseMock):

    def __init__(self, name, session=None, _parent=None):
        session = session or Session()
        super().__init__(name, session, parent=_parent)
        self._has_expectations = False

    def __setattr__(self, name, value):
        if '__setattr__' in self.__dict__:
            return self.__dict__['__setattr__'](name, value)
        else:
            return super().__setattr__(name, value)

    def __getattr__(self, name):
        if '__getattr__' in self.__dict__ :
            return self.__dict__['__getattr__'](name)
        else:
            self.__dict__[name] = tmp = Mock(name, session=self._session, _parent=self)
            return tmp

    def __getattribute__(self, name):
        if name not in ('__getattr__', '__setattr__'):
            return super().__getattribute__(name)
        elif name in self.__dict__:
            return self.__dict__[name]
        elif name == '__getattr__':
            self.__dict__[name] = tmp = _GetAttrMock(self._session, self)
            return tmp
        else:
            self.__dict__[name] = tmp = _SetAttrMock(self._session, self)
            return tmp

    def __call__(self, *args, **kwargs):
        if not self._has_expectations and self._name == _EXPECT_CALL_METHOD_NAME:
            expected_call = Call(self._parent._fullname, *args, **kwargs)
            self._parent._has_expectations = True
            return self._parent._session.expect_call(expected_call)
        else:
            actual_call = Call(self._fullname, *args, **kwargs)
            return self._session(actual_call)


class _GetAttrMock(BaseMock):

    def __init__(self, session, parent):
        super().__init__('__getattr__', session, parent=parent)

    def __call__(self, name):
        actual_call = Call(self._fullname, name)
        return self._session(actual_call)

    def expect_call(self, name):
        if not _utils.is_identifier(name):
            raise TypeError(f"__getattr__.expect_call() must be called with valid Python property name, got {name!r}")
        expected_call = Call(self._fullname, name)
        return self._session.expect_call(expected_call)


class _SetAttrMock(BaseMock):

    def __init__(self, session, parent):
        super().__init__('__setattr__', session, parent=parent)

    def __call__(self, name, value):
        actual_call = Call(self._fullname, name, value)
        return self._session(actual_call)

    def expect_call(self, name, value):
        if not _utils.is_identifier(name):
            raise TypeError(f"__setattr__.expect_call() must be called with valid Python property name, got {name!r}")
        expected_call = Call(self._fullname, name, value)
        return self._session.expect_call(expected_call)

"""
class _ExpectCallProxy:

    def __init__(self, mock):
        self._mock = mock
        self._name_to_method_map = {
            '__getattr__': self._getattr_expect_call,
            '__setattr__': self._setattr_expect_call,
        }

    def __call__(self, *args, **kwargs):
        expect_call = self._name_to_method_map.get(self._mock._name)
        if expect_call is None:
            return self._expect_call(*args, **kwargs)
        else:
            try:
                return expect_call(*args, **kwargs)
            except TypeError as e:
                message_with_replaced_func =\
                    str(e).replace(expect_call.__name__, f"{self._mock._full_name}.expect_call")
                raise TypeError(message_with_replaced_func)

    def _getattr_expect_call(self, name):
        return self._expect_call(name)

    def _setattr_expect_call(self, name, value):
        return self._expect_call(name, value)

    def _expect_call(self, *args, **kwargs):
        expected_call = Call(self._mock._full_name, *args, **kwargs)
        return self._mock._ctx.expect_call(expected_call)


class _Base:

    def __setattr__(self, name, value):
        if '__setattr__' in self.__dict__ and\
           self._is_call_expected(f"{self._full_name}.__setattr__", name, _):
            self.__dict__['__setattr__'](name, value)
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name):
        if '__getattr__' in self.__dict__ and self._is_call_expected(f"{self._full_name}.__getattr__", name):
            return self.__dict__['__getattr__'](name)
        else:
            self.__dict__[name] = tmp = Mock.Attr(self, name)
            return tmp

    def _is_call_expected(self, *args, **kwargs):
        searched_call = Call(*args, **kwargs)
        return self._ctx.expectations.by_call(searched_call).exists()

    def __getattribute__(self, name):
        if name not in ('__getattr__', '__setattr__'):
            return super().__getattribute__(name)
        elif name in self.__dict__:
            return self.__dict__[name]
        else:
            self.__dict__[name] = tmp = Mock.Attr(self, name)
            return tmp


class Mock(_Base):

    class Attr(_Base):

        def __init__(self, parent, name):
            self._parent = parent
            self._name = name
            self.__root = self.__find_root()

        def __find_root(self):
            parent = self._parent
            while parent._parent is not None:
                parent = parent._parent
            return weakref.ref(parent)

        def __repr__(self):
            return f"<mockify.mock.Mock.Attr({self._full_name!r})>"

        def __call__(self, *args, **kwargs):
            if self._ctx.expectations.by_name(self._full_name).exists():
                return self._call(*args, **kwargs)
            elif self._name == 'expect_call':
                return self._expect_call(*args, **kwargs)
            elif self._name == 'assert_satisfied' and self._parent is self._root:
                return self._assert_satisfied(*args, **kwargs)
            else:
                return self._call(*args, **kwargs)

        def _expect_call(self, *args, **kwargs):
            proxy = _ExpectCallProxy(self._parent)
            return proxy(*args, **kwargs)

        def _assert_satisfied(self):
            return self._ctx.expectations.\
                by_name_prefix(self._root._name).\
                assert_satisfied()

        def _call(self, *args, **kwargs):
            actual_call = Call(self._full_name, *args, **kwargs)
            return self._ctx(actual_call)

        @property
        def _parent(self):
            return self.__parent()

        @_parent.setter
        def _parent(self, value):
            self.__parent = weakref.ref(value)

        @property
        def _root(self):
            return self.__root()

        @property
        def _full_name(self):
            return f"{self._parent._full_name}.{self._name}"

        @property
        def _ctx(self):
            return self._root._ctx

    def __init__(self, name, ctx=None):
        self._name = name
        self._parent = None
        self._ctx = ctx or Context()

    def __repr__(self):
        return f"<mockify.mock.{self.__class__.__name__}({self._name!r})>"

    def __call__(self, *args, **kwargs):
        actual_call = Call(self._name, *args, **kwargs)
        return self._ctx(actual_call)

    @property
    def _full_name(self):
        return self._name
"""
