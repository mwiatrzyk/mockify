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

        * Unary arythmethic operators:

            - ``__pos__(self)``, f.e. **+foo**
            - ``__neg__(self)``, f.e. **-foo**
            - ``__abs__(self)``, f.e. **abs(foo)**
            - ``__invert__(self)``, f.e. **~foo**
            - ``__round__(self, ndigits=None)``, f.e. **round(foo)** or **round(foo, ndigits)**
            - ``__floor__(self)``, f.e. **floor(foo)**
            - ``__ceil__(self)``, f.e. **ceil(foo)**

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
    _m_builtin_mocks = {}

    @classmethod
    def _register_builtin_mock(cls, name: str):

        def decorator(mock_factory):
            cls._m_builtin_mocks[name] = mock_factory
            return mock_factory

        return decorator

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

    def _get_mock_or_super(self, name):
        d = self.__dict__
        if name in d:
            return d[name]
        super_method = getattr(super(), name, None)
        if super_method is None:
            return getattr(self, name)
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

    def __hash__(self):
        return self._get_mock_or_super('__hash__')()

    def __sizeof__(self):
        return self._get_mock_or_super('__sizeof__')()

    def __str__(self):
        return self._get_mock_or_super('__str__')()

    def __repr__(self):
        return self._get_mock_or_super('__repr__')()

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

    def __getattr__(self, name):
        dct = self.__dict__
        getattr_mock = dct.get('__getattr__')
        if getattr_mock is not None:
            return getattr_mock(name)
        dct[name] = tmp = FunctionMock(name, parent=self)
        return tmp

    def __setattr__(self, name, value):
        if '__setattr__' in self.__dict__:
            self.__dict__['__setattr__'](name, value)
        else:
            super().__setattr__(name, value)

    def __delattr__(self, name):
        if '__delattr__' in self.__dict__:
            self.__dict__['__delattr__'](name)
        else:
            super().__delattr__(name)

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


@ObjectMock._register_builtin_mock('__getattr__')
@ObjectMock._register_builtin_mock('__delattr__')
class _GetDelAttrMock(FunctionMock):

    def __call__(self, name):
        return super().__call__(name)

    def expect_call(self, name):
        return super().expect_call(name)


@ObjectMock._register_builtin_mock('__getitem__')
@ObjectMock._register_builtin_mock('__delitem__')
@ObjectMock._register_builtin_mock('__contains__')
class _GetDelContainsItemMock(FunctionMock):

    def __call__(self, key):
        return super().__call__(key)

    def expect_call(self, key):
        return super().expect_call(key)


@ObjectMock._register_builtin_mock('__setattr__')
class _SetAttrMock(FunctionMock):

    def __call__(self, name, value):
        return super().__call__(name, value)

    def expect_call(self, name, value):
        return super().expect_call(name, value)


@ObjectMock._register_builtin_mock('__setitem__')
class _SetItemMock(FunctionMock):

    def __call__(self, key, value):
        return super().__call__(key, value)

    def expect_call(self, key, value):
        return super().expect_call(key, value)


@ObjectMock._register_builtin_mock('__iter__')
@ObjectMock._register_builtin_mock('__enter__')
@ObjectMock._register_builtin_mock('__aenter__')
@ObjectMock._register_builtin_mock('__str__')
@ObjectMock._register_builtin_mock('__repr__')
@ObjectMock._register_builtin_mock('__hash__')
@ObjectMock._register_builtin_mock('__sizeof__')
class _NoArgMethodMock(FunctionMock):

    def __call__(self):
        return super().__call__()

    def expect_call(self):
        return super().expect_call()


@ObjectMock._register_builtin_mock('__eq__')
@ObjectMock._register_builtin_mock('__ne__')
@ObjectMock._register_builtin_mock('__lt__')
@ObjectMock._register_builtin_mock('__gt__')
@ObjectMock._register_builtin_mock('__le__')
@ObjectMock._register_builtin_mock('__ge__')
class _CmpMethodMock(FunctionMock):

    def __call__(self, other):
        return super().__call__(other)

    def expect_call(self, other):
        return super().expect_call(other)


@ObjectMock._register_builtin_mock('__pos__')
@ObjectMock._register_builtin_mock('__neg__')
@ObjectMock._register_builtin_mock('__abs__')
@ObjectMock._register_builtin_mock('__invert__')
@ObjectMock._register_builtin_mock('__floor__')
@ObjectMock._register_builtin_mock('__ceil__')
@ObjectMock._register_builtin_mock('__trunc__')
class _UnaryMethodMock(FunctionMock):

    def __call__(self):
        return super().__call__()

    def expect_call(self):
        return super().expect_call()


@ObjectMock._register_builtin_mock('__round__')
class _RoundMethodMock(FunctionMock):

    def __call__(self, ndigits=None):
        return super().__call__(ndigits=ndigits)

    def expect_call(self, ndigits=None):
        return super().expect_call(ndigits=ndigits)
