import sys
import math
import weakref
import warnings

from mockify import _utils, Registry

from .function import Function


class _Attribute:

    def __init__(self, name, owner):
        self._name = name
        self._owner = owner

    @property
    def _owner(self):
        return self.__owner()

    @_owner.setter
    def _owner(self, value):
        self.__owner = weakref.ref(value)

    @property
    def _registry(self):
        return self._owner._registry

    @property
    def name(self):
        return f"{self._owner.name}.{self._name}"

    def _has_property(self, name):
        return name in self.__dict__


class Object:
    """Class for mocking Python objects.

    .. versionchanged:: 0.5
        New API introduced.

    .. versionadded:: 0.3

    .. testsetup::

        from mockify.mock import Object
        from mockify.actions import Return

    Since version 0.5 this class provides a new API that complies with the
    one used by other mock classes.

    You can now create mock objects directly, without subclassing:

    .. testcode::

        mock = Object('mock')

    Method calls are now recorded like this:

    .. testcode::

        mock.foo.expect_call(1, 2)

    And for recording property get/set expectations you write:

    .. testcode::

        mock.bar.fset.expect_call(123)
        mock.bar.fget.expect_call().will_once(Return(123))
        mock.baz.fget.expect_call().will_once(Return(456))

    And you can still subclass this class and provide a set of methods and
    properties, like in this example:

    .. testcode::

        class Dummy(Object):
            __methods__ = ['foo']
            __properties__ = ['bar']

    :param name:
        Name of mocked object

    :param methods:
        Sequence of names of methods to be mocked.

        If this is given, then the only allowed methods will be the ones from
        given sequence. Attempt to access any other will result in
        :exc:`AttributeError` being raised.

    :param properties:
        Sequence of names of properties to be mocked.

        Use is the same as for **methods** parameter.

    :param registry:
        Instance of :class:`mockify.Registry` class.

        If not given, a default one will be created for this mock object.
    """

    class Method(_Attribute):

        @_utils.memoized_property
        def _mock(self):
            return Function(self.name, registry=self._registry)

        def __call__(self, *args, **kwargs):
            return self._mock(*args, **kwargs)

        def expect_call(self, *args, **kwargs):
            return self._mock.expect_call(*args, **kwargs)

    class _PropertyMeta(type):
        _proxy_magic_methods = (
            '__repr__', '__str__', '__eq__', '__ne__', '__lt__', '__gt__',
            '__le__', '__ge__', '__pos__', '__neg__', '__abs__',
            '__invert__', '__round__', '__trunc__', '__add__', '__sub__',
            '__mul__', '__floordiv__', '__truediv__', '__mod__',
            '__divmod__', '__pow__', '__lshift__', '__rshift__', '__and__',
            '__or__', '__xor__', '__radd__', '__rsub__', '__rmul__',
            '__rfloordiv__', '__rtruediv__', '__rmod__', '__rdivmod__',
            '__rpow__', '__rlshift__', '__rrshift__', '__rand__', '__ror__',
            '__rxor__', '__format__', '__hash__', '__dir__', '__len__',
            '__getitem__', '__setitem__', '__delitem__', '__contains__',
            '__iter__',
        )

        def __init__(cls, name, bases, attrs):

            def make_method(name):

                def proxy(self, *args, **kwargs):
                    return getattr(self._value, name)(*args, **kwargs)

                proxy.__name__ = name
                return proxy

            for name in cls._proxy_magic_methods:
                setattr(cls, name, make_method(name))

    class Property(_Attribute, metaclass=_PropertyMeta):

        class Setter(_Attribute):

            @_utils.memoized_property
            def _mock(self):
                return Function(self.name, registry=self._registry)

            def expect_call(self, value):
                return self._mock.expect_call(value)

        class Getter(_Attribute):

            @_utils.memoized_property
            def _mock(self):
                return Function(self.name, registry=self._registry)

            def expect_call(self):
                return self._mock.expect_call()

        def __int__(self):
            return int(self._value)

        def __float__(self):
            return float(self._value)

        def __complex__(self):
            return complex(self._value)

        def __bool__(self):
            return bool(self._value)

        def __nonzero__(self):
            return self.__bool__()

        def __getattr__(self, name):
            return getattr(self._value, name)

        def __call__(self, *args, **kwargs):
            return self._value(*args, **kwargs)

        @_utils.memoized_property
        def fget(self):
            return self.Getter('fget', self)

        @_utils.memoized_property
        def fset(self):
            return self.Setter('fset', self)

        @_utils.memoized_property
        def _value(self):
            return self.fget._mock()

        def expect_call(self, *args, **kwargs):
            method = self._make_specific(self._owner, self._name, Object.Method)
            return method.expect_call(*args, **kwargs)

        def _make_specific(self, obj, attr_name, attr_type):
            d = obj.__dict__
            if not isinstance(d[attr_name], attr_type):
                d[attr_name] = attr_type(attr_name, obj)
            return d[attr_name]

    __methods__ = tuple()
    __properties__ = tuple()

    def __init__(self, name, methods=None, properties=None, registry=None):
        self._name = name
        self._methods = tuple(methods or self.__methods__)
        self._properties = tuple(properties or self.__properties__)
        self._allowed_attrs = self._methods + self._properties
        self._registry = registry or Registry()
        if self._methods:
            self._initialize_predefined_methods()
        if self._properties:
            self._initialize_predefined_properties()

    def _initialize_predefined_methods(self):
        for name in self._methods:
            self.__dict__[name] = self.Method(name, self)

    def _initialize_predefined_properties(self):
        for name in self._properties:
            self.__dict__[name] = self.Property(name, self)

    def __getattr__(self, name):
        if self._allowed_attrs and name not in self._allowed_attrs:
            raise AttributeError(f"Mock object {self._name!r} has no attribute {name!r}")
        self.__dict__[name] = tmp = self.Property(name, self)
        return tmp

    def __getattribute__(self, name):
        if name.startswith('_'):
            return super().__getattribute__(name)
        else:
            d = self.__dict__
            if name in d and isinstance(d[name], Object.Property):
                if '_value' in d[name].__dict__:
                    del d[name].__dict__['_value']
                return d[name]
            else:
                return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return super().__setattr__(name, value)
        elif self._properties and name not in self._properties:
            raise AttributeError(f"Mock object {self._name!r} does not allow setting attribute {name!r}")
        else:
            self.__dict__[name] = tmp = self.Property(name, self)
            return tmp.fset._mock(value)

    @property
    def _mocks(self):
        for k, v in self.__dict__.items():
            if isinstance(v, self.Method):
                yield v._mock
            elif isinstance(v, self.Property):
                if v._has_property('fset'):
                    yield v.fset._mock
                if v._has_property('fget'):
                    yield v.fget._mock

    @property
    def name(self):
        return self._name

    def expect_call(self, __name__, *args, **kwargs):
        """Record method call expectation.

        .. deprecated:: 0.5
            See :class:`Object` for a brief example of how to use new API.
        """
        warnings.warn(
            "Object.expect_call('example', ...) is deprecated "
            "since version 0.5 - use Object.example.expect_call(...) "
            "instead.", DeprecationWarning)
        return getattr(self, __name__).expect_call(*args, **kwargs)

    def expect_set(self, __name__, value):
        """Record property set expectation.

        .. deprecated:: 0.5
            See :class:`Object` for a brief example of how to use new API.
        """
        warnings.warn(
            "Object.expect_set('example', value) is deprecated "
            "since version 0.5 - use Object.example.fset.expect_call(value) "
            "instead.", DeprecationWarning
        )
        return getattr(self, __name__).fset.expect_call(value)

    def expect_get(self, __name__):
        """Record property get expectation.

        .. deprecated:: 0.5
            See :class:`Object` for a brief example of how to use new API.
        """
        warnings.warn(
            "Object.expect_get('example') is deprecated "
            "since version 0.5 - use Object.example.fget.expect_call() "
            "instead.", DeprecationWarning
        )
        return getattr(self, __name__).fget.expect_call()

    def assert_satisfied(self):
        """Assert that all expected method/property calls are satisfied."""
        self._registry.assert_satisfied(*[m.name for m in self._mocks])
