import weakref
import itertools

from . import _utils
from ._call import Call
from ._context import Context
from .matchers import _

_next_mock_id = itertools.count()


class MockFactory:

    def __init__(self, ctx=None):
        self._ctx = ctx or Context()
        self._created_mocks = []

    def __call__(self, name):
        mock = Mock(name, self)
        self._created_mocks.append(mock)
        return mock

    def done(self):
        self._ctx.assert_satisfied()


class MockInfo:

    def __init__(self, mock):
        self._mock = mock

    def __repr__(self):
        return f"<mockify._MockInfo({self._mock!r})>"

    @property
    def ctx(self):
        return self.factory._ctx

    @property
    def name(self):
        return self._mock._fullname

    @property
    def factory(self):
        return self._mock._factory

    @property
    def expectations(self):
        return self.ctx.expectations.by_name(self._mock._fullname)

    @property
    def children(self):
        for name, obj in self._mock.__dict__.items():
            if isinstance(obj, Mock):
                if not obj._is_method():
                    yield obj
                yield from self.__class__(obj).children


class Mock:
    _EXPECT_CALL_METHOD = 'expect_call'

    def __init__(self, name, factory, _parent=None):
        self._name = name
        self._factory = factory
        self._parent = _parent
        self._method_name = None

    def __repr__(self):
        return f"<mockify._Mock({self._fullname!r})>"

    def __getattr__(self, name):
        self.__dict__[name] = tmp = Mock(name, self._factory, _parent=self)
        return tmp

    def __call__(self, *args, **kwargs):
        if self._name == self._EXPECT_CALL_METHOD:
            expected_call = Call(self._parent._fullname, *args, **kwargs)
            self._method_name = self._EXPECT_CALL_METHOD
            return self._parent._ctx.expect_call(expected_call)
        else:
            actual_call = Call(self._fullname, *args, **kwargs)
            return self._ctx(actual_call)

    @property
    def _factory(self):
        return self.__factory()

    @_factory.setter
    def _factory(self, value):
        self.__factory = weakref.ref(value)

    @property
    def _ctx(self):
        return self._factory._ctx

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

    def _is_method(self):
        return self._method_name is not None


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
