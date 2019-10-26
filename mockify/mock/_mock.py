import weakref

from .. import _utils, Call, Context
from ..matchers import _
from ._function import Function


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


class Mock:

    def __init__(self, name, ctx=None, _parent=None):
        self._name = name
        self._ctx = ctx or Context()
        self._parent = _parent
        self._func = Function(self._fullname, ctx=self._ctx)

    def __repr__(self):
        return f"<mockify.mock.Mock({self._name!r})>"

    def __getattr__(self, name):
        self.__dict__[name] = tmp = Mock(name, ctx=self._ctx, _parent=self)
        return tmp

    def __call__(self, *args, **kwargs):
        parent = self._parent
        if self._name == 'expect_call' and parent is not None:
            return parent._func.expect_call(*args, **kwargs)
        else:
            return self._func(*args, **kwargs)

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
