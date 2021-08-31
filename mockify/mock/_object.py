from collections.abc import Mapping

from mockify.interface import IMock

from ._function import FunctionMock


# TODO: Add method, readable and writable property lists to this class
# constructor. Methods should allow the user to pass his/her own mock instance
# as method implementation (similar to the way as built-in mocks are done)

class ObjectMock(FunctionMock):
    """A class for mocking Python objects.

    With this class you will be able to mock any Python object containing
    user-defined methods, magic methods (see the list of supported below) or
    both.

    Currently supported magic methods are:

        * Comparison operators:

            - ``__eq__(self, other)``, i.e. **==**
            - ``__ne__(self, other)``, i.e. **!=**
            - ``__lt__(self, other)``, i.e. **<**
            - ``__gt__(self, other)``, i.e. **>**
            - ``__le__(self, other)``, i.e. **<=**
            - ``__ge__(self, other)``, i.e. **>=**

        * Unary arithmethic operators:

            - ``__pos__(self)``, f.e. **+foo**
            - ``__neg__(self)``, f.e. **-foo**
            - ``__abs__(self)``, f.e. **abs(foo)**
            - ``__invert__(self)``, f.e. **~foo**
            - ``__round__(self, ndigits=None)``, f.e. **round(foo)** or **round(foo, ndigits)**
            - ``__floor__(self)``, f.e. **floor(foo)**
            - ``__ceil__(self)``, f.e. **ceil(foo)**

        * Normal arithmethic operators, including reflected versions for all
          listed below (f.e.  ``__radd__`` for ``__add__``, which will be
          called in **other + foo** statement, as opposed to typical **foo +
          other**):

            - ``__add__(self, other)__``, f.e. **foo + other**
            - ``__sub__(self, other)__``, f.e. **foo - other**
            - ``__mul__(self, other)__``, f.e. **foo * other**
            - ``__floordiv__(self, other)__``, f.e. **foo // other**
            - ``__div__`` and ``__truediv__``, f.e. **foo / other**
            - ``__mod__(self, other)__``, f.e. **foo % other**
            - ``__divmod__(self, other)__``, f.e. **divmod(foo, other)**
            - ``__pow__(self, other)__``, f.e. ``foo ** other``
            - ``__lshift__(self, other)``, f.e. **foo << other**
            - ``__rshift__(self, other)``, f.e. **foo >> other**
            - ``__and__(self, other)``, f.e. **foo & other**
            - ``__or__(self, other)``, f.e. **foo | other**
            - ``__xor__(self, other)``, f.e. **foo ^ other**

        * In-place arithmethic operators:

            - ``__iadd__(self, other)__``, f.e. **foo += other**
            - ``__isub__(self, other)__``, f.e. **foo -= other**
            - ``__imul__(self, other)__``, f.e. **foo *= other**
            - ``__ifloordiv__(self, other)__``, f.e. **foo //= other**
            - ``__idiv__`` and ``__itruediv__``, f.e. **foo /= other**
            - ``__imod__(self, other)__``, f.e. **foo %= other**
            - ``__ipow__(self, other)__``, f.e. ``foo **= other``
            - ``__ilshift__(self, other)``, f.e. **foo <<= other**
            - ``__irshift__(self, other)``, f.e. **foo >>= other**
            - ``__iand__(self, other)``, f.e. **foo &= other**
            - ``__ior__(self, other)``, f.e. **foo |= other**
            - ``__ixor__(self, other)``, f.e. **foo ^= other**

    Here are some examples of how to use this class:

        1. Mocking normal methods:

            .. testcode::

                from mockify.api import ObjectMock, Return, satisfied

                def func(obj):
                    return obj.foo(1, 2, 3)

                def test_func():
                    obj = ObjectMock('obj')
                    obj.foo.expect_call(1, 2, 3).will_once(Return(123))
                    with satisfied(obj):
                        assert func(obj) == 123

            .. testcode::
                :hide:

                test_func()

        2. Mocking callable objects:

            .. testcode::

                from mockify.api import ObjectMock, Return, satisfied

                def func(obj):
                    return obj(1, 2, 3)

                def test_func():
                    obj = ObjectMock('obj')
                    obj.expect_call(1, 2, 3).will_once(Return(123))
                    with satisfied(obj):
                        assert func(obj) == 123

            .. testcode::
                :hide:

                test_func()

        3. Mocking dunder methods:

            .. testcode::

                from mockify.api import ObjectMock, Return, satisfied

                def setdefault(d, k, v):
                    if k not in d:
                        d[k] = v
                        return v
                    return d[k]

                def test_setdefault_with_existing_item():
                    obj = ObjectMock('obj')
                    obj.__contains__.expect_call('foo').will_once(Return(True))
                    obj.__getitem__.expect_call('foo').will_once(Return('spam'))
                    with satisfied(obj):
                        assert setdefault(obj, 'foo', 123) == 'spam'

                def test_setdefault_with_non_existing_item():
                    obj = ObjectMock('obj')
                    obj.__contains__.expect_call('foo').will_once(Return(False))
                    obj.__setitem__.expect_call('foo', 123)
                    with satisfied(obj):
                        assert setdefault(obj, 'foo', 123) == 123

            .. testcode::
                :hide:

                test_setdefault_with_existing_item()
                test_setdefault_with_non_existing_item()

    .. versionadded:: (unreleased)
    """

    class _MockClassRegistry(Mapping):

        def __init__(self):
            self._storage = {}

        def __getitem__(self, key):
            return self._storage[key]

        def __iter__(self):
            return iter(self._storage)

        def __len__(self):
            return len(self._storage)

        def register(self, name):

            def decorator(mock_factory):
                self._storage[name] = mock_factory
                return mock_factory

            return decorator

    _m_builtin_mocks = _MockClassRegistry()

    def __getattribute__(self, name):
        if name == '_m_builtin_mocks':
            return super().__getattribute__(name)
        method_mocks = self._m_builtin_mocks
        if name not in method_mocks:
            return super().__getattribute__(name)
        dct = self.__dict__
        if name in dct:
            return dct[name]
        dct[name] = tmp = method_mocks[name](name, parent=self)
        return tmp

    def _get_mock_or_super(self, name, aliases=None):
        d = self.__dict__
        if name in d:
            return d[name]
        for alias in (aliases or []):
            if alias in d:
                return d[alias]
        super_method = getattr(super(), name, None)
        if super_method is None:
            return self.__getattribute__(name)
        return super_method

    def __eq__(self, other):
        return self._get_mock_or_super('__eq__')(other)

    def __ne__(self, other):
        return self._get_mock_or_super('__ne__')(other)

    def __lt__(self, other):
        return self._get_mock_or_super('__lt__')(other)

    def __gt__(self, other):
        return self._get_mock_or_super('__gt__')(other)

    def __le__(self, other):
        return self._get_mock_or_super('__le__')(other)

    def __ge__(self, other):
        return self._get_mock_or_super('__ge__')(other)

    def __pos__(self):
        return self._get_mock_or_super('__pos__')()

    def __neg__(self):
        return self._get_mock_or_super('__neg__')()

    def __abs__(self):
        return self._get_mock_or_super('__abs__')()

    def __invert__(self):
        return self._get_mock_or_super('__invert__')()

    def __round__(self, ndigits=None):
        return self._get_mock_or_super('__round__')(ndigits=ndigits)

    def __floor__(self):
        return self._get_mock_or_super('__floor__')()

    def __ceil__(self):
        return self._get_mock_or_super('__ceil__')()

    def __trunc__(self):
        return self._get_mock_or_super('__trunc__')()

    def __add__(self, other):
        return self._get_mock_or_super('__add__')(other)

    def __sub__(self, other):
        return self._get_mock_or_super('__sub__')(other)

    def __mul__(self, other):
        return self._get_mock_or_super('__mul__')(other)

    def __floordiv__(self, other):
        return self._get_mock_or_super('__floordiv__')(other)

    def __truediv__(self, other):
        return self._get_mock_or_super('__truediv__', aliases=['__div__'])(other)

    def __mod__(self, other):
        return self._get_mock_or_super('__mod__')(other)

    def __divmod__(self, other):
        return self._get_mock_or_super('__divmod__')(other)

    def __pow__(self, other):
        return self._get_mock_or_super('__pow__')(other)

    def __lshift__(self, other):
        return self._get_mock_or_super('__lshift__')(other)

    def __rshift__(self, other):
        return self._get_mock_or_super('__rshift__')(other)

    def __and__(self, other):
        return self._get_mock_or_super('__and__')(other)

    def __or__(self, other):
        return self._get_mock_or_super('__or__')(other)

    def __xor__(self, other):
        return self._get_mock_or_super('__xor__')(other)

    def __radd__(self, other):
        return self._get_mock_or_super('__radd__')(other)

    def __rsub__(self, other):
        return self._get_mock_or_super('__rsub__')(other)

    def __rmul__(self, other):
        return self._get_mock_or_super('__rmul__')(other)

    def __rfloordiv__(self, other):
        return self._get_mock_or_super('__rfloordiv__')(other)

    def __rtruediv__(self, other):
        return self._get_mock_or_super('__rtruediv__', aliases=['__rdiv__'])(other)

    def __rmod__(self, other):
        return self._get_mock_or_super('__rmod__')(other)

    def __rdivmod__(self, other):
        return self._get_mock_or_super('__rdivmod__')(other)

    def __rpow__(self, other):
        return self._get_mock_or_super('__rpow__')(other)

    def __rlshift__(self, other):
        return self._get_mock_or_super('__rlshift__')(other)

    def __rrshift__(self, other):
        return self._get_mock_or_super('__rrshift__')(other)

    def __rand__(self, other):
        return self._get_mock_or_super('__rand__')(other)

    def __ror__(self, other):
        return self._get_mock_or_super('__ror__')(other)

    def __rxor__(self, other):
        return self._get_mock_or_super('__rxor__')(other)

    def __iadd__(self, other):
        return self._get_mock_or_super('__iadd__')(other)

    def __isub__(self, other):
        return self._get_mock_or_super('__isub__')(other)

    def __imul__(self, other):
        return self._get_mock_or_super('__imul__')(other)

    def __ifloordiv__(self, other):
        return self._get_mock_or_super('__ifloordiv__')(other)

    def __itruediv__(self, other):
        return self._get_mock_or_super('__itruediv__', aliases=['__idiv__'])(other)

    def __imod__(self, other):
        return self._get_mock_or_super('__imod__')(other)

    def __ipow__(self, other):
        return self._get_mock_or_super('__ipow__')(other)

    def __ilshift__(self, other):
        return self._get_mock_or_super('__ilshift__')(other)

    def __irshift__(self, other):
        return self._get_mock_or_super('__irshift__')(other)

    def __iand__(self, other):
        return self._get_mock_or_super('__iand__')(other)

    def __ior__(self, other):
        return self._get_mock_or_super('__ior__')(other)

    def __ixor__(self, other):
        return self._get_mock_or_super('__ixor__')(other)

    def __int__(self):
        return self._get_mock_or_super('__int__')()

    def __float__(self):
        return self._get_mock_or_super('__float__')()

    def __complex__(self):
        return self._get_mock_or_super('__complex__')()

    def __bool__(self):
        return self._get_mock_or_super('__bool__')()

    def __index__(self):
        return self._get_mock_or_super('__index__')()

    def __str__(self):
        return self._get_mock_or_super('__str__')()

    def __repr__(self):
        return self._get_mock_or_super('__repr__')()

    def __format__(self, formatstr):
        return self._get_mock_or_super('__format__')(formatstr)

    def __hash__(self):
        return self._get_mock_or_super('__hash__')()

    def __dir__(self):
        return self._get_mock_or_super('__dir__')()

    def __sizeof__(self):
        return self._get_mock_or_super('__sizeof__')()

    def __getattr__(self, name):
        d = self.__dict__
        getattr_mock = d.get('__getattr__')
        if getattr_mock is not None:
            return getattr_mock(name)
        d[name] = tmp = FunctionMock(name, parent=self)
        return tmp

    def __setattr__(self, name, value):
        return self._get_mock_or_super('__setattr__')(name, value)

    def __delattr__(self, name):
        return self._get_mock_or_super('__delattr__')(name)

    def __len__(self):
        d = self.__dict__
        if '__len__' in d:
            return d['__len__']()
        super_method = getattr(super(), '__len__', None)
        if super_method is not None:
            return super_method()
        return NotImplemented

    def __iter__(self):
        return getattr(self, '__iter__')()

    def __contains__(self, key):
        return getattr(self, '__contains__')(key)

    def __enter__(self):
        return getattr(self, '__enter__')()

    async def __aenter__(self):
        return getattr(self, '__aenter__')()

    def __exit__(self, exc_type, exc, tb):
        pass

    async def __aexit__(self, exc_type, exc, tb):
        pass

    def __getitem__(self, name):
        if '__getitem__' in self.__dict__:
            return getattr(self, '__getitem__')(name)
        return self.__dict__.setdefault('__m_items', {})[name]

    def __setitem__(self, name, value):
        if '__setitem__' in self.__dict__:
            self.__dict__['__setitem__'](name, value)
        else:
            self.__dict__.setdefault('__m_items', {})[name] = value

    def __delitem__(self, name):
        if '__delitem__' in self.__dict__:
            getattr(self, '__delitem__')(name)
        else:
            del self.__dict__.setdefault('__m_items', {})[name]

    def __m_children__(self):
        for item in self.__dict__.values():
            if isinstance(item, IMock):
                yield item

    @_m_builtin_mocks.register('__getattr__')
    @_m_builtin_mocks.register('__delattr__')
    class _GetDelAttrMock(FunctionMock):

        def __call__(self, name):
            return super().__call__(name)

        def expect_call(self, name):
            return super().expect_call(name)

    @_m_builtin_mocks.register('__getitem__')
    @_m_builtin_mocks.register('__delitem__')
    @_m_builtin_mocks.register('__contains__')
    class _GetDelContainsItemMock(FunctionMock):

        def __call__(self, key):
            return super().__call__(key)

        def expect_call(self, key):
            return super().expect_call(key)

    @_m_builtin_mocks.register('__setattr__')
    class _SetAttrMock(FunctionMock):

        def __call__(self, name, value):
            return super().__call__(name, value)

        def expect_call(self, name, value):
            return super().expect_call(name, value)

    @_m_builtin_mocks.register('__setitem__')
    class _SetItemMock(FunctionMock):

        def __call__(self, key, value):
            return super().__call__(key, value)

        def expect_call(self, key, value):
            return super().expect_call(key, value)

    @_m_builtin_mocks.register('__iter__')
    @_m_builtin_mocks.register('__enter__')
    @_m_builtin_mocks.register('__aenter__')
    @_m_builtin_mocks.register('__str__')
    @_m_builtin_mocks.register('__repr__')
    @_m_builtin_mocks.register('__hash__')
    @_m_builtin_mocks.register('__sizeof__')
    @_m_builtin_mocks.register('__int__')
    @_m_builtin_mocks.register('__float__')
    @_m_builtin_mocks.register('__complex__')
    @_m_builtin_mocks.register('__bool__')
    @_m_builtin_mocks.register('__index__')
    @_m_builtin_mocks.register('__dir__')
    @_m_builtin_mocks.register('__len__')
    class _NoArgMethodMock(FunctionMock):

        def __call__(self):
            return super().__call__()

        def expect_call(self):
            return super().expect_call()

    @_m_builtin_mocks.register('__eq__')
    @_m_builtin_mocks.register('__ne__')
    @_m_builtin_mocks.register('__lt__')
    @_m_builtin_mocks.register('__gt__')
    @_m_builtin_mocks.register('__le__')
    @_m_builtin_mocks.register('__ge__')
    @_m_builtin_mocks.register('__add__')
    @_m_builtin_mocks.register('__sub__')
    @_m_builtin_mocks.register('__mul__')
    @_m_builtin_mocks.register('__floordiv__')
    @_m_builtin_mocks.register('__div__')
    @_m_builtin_mocks.register('__truediv__')
    @_m_builtin_mocks.register('__mod__')
    @_m_builtin_mocks.register('__divmod__')
    @_m_builtin_mocks.register('__pow__')
    @_m_builtin_mocks.register('__lshift__')
    @_m_builtin_mocks.register('__rshift__')
    @_m_builtin_mocks.register('__and__')
    @_m_builtin_mocks.register('__or__')
    @_m_builtin_mocks.register('__xor__')
    @_m_builtin_mocks.register('__radd__')
    @_m_builtin_mocks.register('__rsub__')
    @_m_builtin_mocks.register('__rmul__')
    @_m_builtin_mocks.register('__rfloordiv__')
    @_m_builtin_mocks.register('__rdiv__')
    @_m_builtin_mocks.register('__rtruediv__')
    @_m_builtin_mocks.register('__rmod__')
    @_m_builtin_mocks.register('__rdivmod__')
    @_m_builtin_mocks.register('__rpow__')
    @_m_builtin_mocks.register('__rlshift__')
    @_m_builtin_mocks.register('__rrshift__')
    @_m_builtin_mocks.register('__rand__')
    @_m_builtin_mocks.register('__ror__')
    @_m_builtin_mocks.register('__rxor__')
    @_m_builtin_mocks.register('__iadd__')
    @_m_builtin_mocks.register('__isub__')
    @_m_builtin_mocks.register('__imul__')
    @_m_builtin_mocks.register('__ifloordiv__')
    @_m_builtin_mocks.register('__idiv__')
    @_m_builtin_mocks.register('__itruediv__')
    @_m_builtin_mocks.register('__imod__')
    @_m_builtin_mocks.register('__ipow__')
    @_m_builtin_mocks.register('__ilshift__')
    @_m_builtin_mocks.register('__irshift__')
    @_m_builtin_mocks.register('__iand__')
    @_m_builtin_mocks.register('__ior__')
    @_m_builtin_mocks.register('__ixor__')
    class _BinaryOperatorMock(FunctionMock):

        def __call__(self, other):
            return super().__call__(other)

        def expect_call(self, other):
            return super().expect_call(other)

    @_m_builtin_mocks.register('__pos__')
    @_m_builtin_mocks.register('__neg__')
    @_m_builtin_mocks.register('__abs__')
    @_m_builtin_mocks.register('__invert__')
    @_m_builtin_mocks.register('__floor__')
    @_m_builtin_mocks.register('__ceil__')
    @_m_builtin_mocks.register('__trunc__')
    class _UnaryOperatorMock(FunctionMock):

        def __call__(self):
            return super().__call__()

        def expect_call(self):
            return super().expect_call()

    @_m_builtin_mocks.register('__round__')
    class _RoundOperatorMock(FunctionMock):

        def __call__(self, ndigits=None):
            return super().__call__(ndigits=ndigits)

        def expect_call(self, ndigits=None):
            return super().expect_call(ndigits=ndigits)

    @_m_builtin_mocks.register('__format__')
    class _FormatMock(FunctionMock):

        def __call__(self, formatstr):
            return super().__call__(formatstr)

        def expect_call(self, formatstr):
            return super().expect_call(formatstr)
