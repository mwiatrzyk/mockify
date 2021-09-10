# ---------------------------------------------------------------------------
# mockify/mock/_mock.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring

from mockify import _utils
from mockify.abc import IMock

from ._base import BaseMock
from ._function import BaseFunctionMock, FunctionMock

__all__ = export = _utils.ExportList()  # pylint: disable=invalid-all-format


def _register_builtin_mock(name):

    def decorator(cls):
        if not hasattr(cls, '_m_method_names'):
            cls._m_method_names = set()  # pylint: disable=protected-access
        cls._m_method_names.add(name)  # pylint: disable=protected-access
        return cls

    return decorator


# TODO: Add method, readable and writable property lists to this class
# constructor. Methods should allow the user to pass his/her own mock instance
# as method implementation (similar to the way as built-in mocks are done)


@export
class Mock(FunctionMock):
    """General purpose mocking class.

    This class can be used to:

    * create mocks of free functions (f.e. callbacks) or callable objects,
    * create mocks of any Python objects
    * create mocks of namespaced function calls (f.e. ``foo.bar.baz.spam(...)``),
    * create ad-hoc data objects.

    No matter what you will be mocking, for all cases creating mock objects
    is always the same - by giving it a *name* and optionally *session*. Mock
    objects automatically create attributes on demand, and that attributes
    form some kind of **nested** or **child** mocks.

    To record expectations, you have to call **expect_call()** method on one
    of that attributes, or on mock object itself (for function mocks). Then
    you pass mock object to unit under test. Finally, you will need
    :func:`mockify.core.assert_satisfied` function or :func:`mockify.core.satisfied`
    context manager to check if the mock is satisfied.

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

    * Type conversion operators:

        - ``__str__(self)``, f.e. **str(foo)**
        - ``__int__(self)``, f.e. **int(foo)**
        - ``__float__(self)``, f.e. **float(foo)**
        - ``__complex__(self)``, f.e. **complex(foo)**
        - ``__index__(self)``, f.e. **oct(foo)**, **hex(foo)** or when used
            in slice expression

    * Class representation methods:

        - ``__repr__(self)``, f.e. **repr(foo)**
        - ``__format__(self, formatstr)``, used when :meth:`str.format` is
            given an instance of a mock (*formatstr* is then passed from
            formatting options, f.e. ``"{:abc}".format(foo)`` will pass
            **abc** as *formatstr*)
        - ``__hash__(self)``, called by built-in :func:`hash`
        - ``__dir__(self)``, called by built-in :func:`dir`
        - ``__sizeof__(self)``, called by :func:`sys.getsizeof`

    * Attribute access methods:

        - ``__getattr__(self, name)``, used by :func:`getattr` or when
            attribute is being get (f.e. ``spam = foo.spam``)
        - ``__setattr__(self, name, value)``, used by :func:`setattr` or
            when attribute is being set (f.e. ``foo.spam = 123``)
        - ``__delattr__(self, name)``, used by :func:`delattr` or  when
            when attrbute is being deleted (f.e. ``del foo.spam``)

        .. note::

            If the methods above are not mocked, default implementations
            will be used, allowing to set/get/delete a user-defined
            attributes:

            .. testcode::
                :hide:

                from mockify.api import Mock, Return, satisfied

            .. doctest::

                >>> foo = Mock('foo')
                >>> foo.spam = 123
                >>> foo.spam
                123
                >>> del foo.spam

            However, if explicit expectation is set, the behaviour from
            above will be replaced with calling adequate mock object:

            .. testcode::

                foo = Mock('foo')
                foo.__getattr__.expect_call('spam').will_once(Return(123))
                with satisfied(foo):
                    assert foo.spam == 123

    * Container methods:

        - ``__len__(self)``, called by :func:`len`
        - ``__getitem__(self, key)``, called when item is being get (f.e.
            ``spam = foo['spam']``)
        - ``__setitem__(self, key, value)``, called when item is being set
            (f.e. ``foo['spam'] = 123``)
        - ``__delitem__(self, key)``, called when item is being deleted
            (f.e. ``del foo['spam']``)
        - ``__reversed__(self)``, called by :func:`reversed`
        - ``__contains__(self, key)``, called when mock is tested for
            presence of given item (f.e. ``if 'spam' in foo:``)

    * Generator methods:

        - ``__iter__(self)``, called by :func:`iter` or when iterating over
            mock object
        - ``__next__(self)``, called by :func:`next`
        - ``__aiter__(self)``, called when *asynchronous generator* is
            created, f.e. used by ``async for`` statement
        - ``__anext__(self)``, called to advance an *asynchronous generator*

    * **__call__** method:

        - ``__call__(self, *args, **kwargs)``

        .. note::

            Recording expectation explicitly on :meth:`object.__call__`
            magic method is equivalent to recording call expectation
            directly on a mock object:

            .. testcode::

                foo = Mock('foo')
                foo.__call__.expect_call('one').will_once(Return(1))
                foo.expect_call('two').will_once(Return(2))
                with satisfied(foo):
                    assert foo('one') == 1
                    assert foo('two') == 2

    * Context management methods:

        - ``__enter__(self)``
        - ``__aenter__(self)``
        - ``__exit__(self, exc, exc_type, tb)``
        - ``__aexit__(self, exc, exc_type, tb)``

    * Descriptor methods:

        - ``__get__(self, obj, obj_type)``
        - ``__set__(self, obj, value)``
        - ``__delete__(self, obj)``

    Here's an example:

    .. testcode::

        from mockify.core import satisfied
        from mockify.mock import Mock

        def caller(func, a, b):
            func(a + b)

        def test_caller():
            func = Mock('func')
            func.expect_call(5)
            with satisfied(func):
                caller(func, 2, 3)

    .. testcode::
        :hide:

        test_caller()

    See :ref:`creating-mocks` for more details.

    .. versionchanged:: 0.13

        Changelog:

        * Now :class:`Mock` inherits from :class:`mockify.mock.FunctionMock` to
          avoid code duplication

        * Added *max_depth* parameter

        * Added support for (almost) all magic methods

    .. versionchanged:: 0.8
        Now this class inherits from :class:`mockify.mock.BaseMock`

    .. versionadded:: 0.6
    """

    def __new__(cls, name, max_depth=-1, **kwargs):
        if max_depth == 0:
            return FunctionMock(name, **kwargs)
        return super().__new__(cls)

    def __init__(self, name, max_depth=-1, **kwargs):
        super().__init__(name, **kwargs)
        self._m_max_depth = max_depth

    @_utils.memoized_property
    def _m_builtin_mocks(self):
        result = {}
        for mock in self.__class__.__dict__.values():
            if hasattr(mock, '_m_method_names'):
                for n in mock._m_method_names:  # pylint: disable=protected-access
                    result[n] = mock
        return result

    def __getattribute__(self, name):
        if name in ('_m_builtin_mocks', '__class__', '__dict__'):
            return super().__getattribute__(name)
        method_mocks = self._m_builtin_mocks
        if name not in method_mocks:
            return super().__getattribute__(name)
        d = self.__dict__
        if name in d:
            return d[name]
        d[name] = tmp = method_mocks[name](name, parent=self)
        return tmp

    def _get_mock_or_super(self, name, aliases=None, create_if_missing=True):
        d = self.__dict__
        if name in d:
            return d[name]
        for alias in (aliases or []):
            if alias in d:
                return d[alias]
        super_method = getattr(super(), name, None)
        if super_method is None and create_if_missing:
            return self.__getattribute__(name)
        return super_method

    def __eq__(self, other):
        method = self._get_mock_or_super('__eq__', create_if_missing=False)
        if method is not None:
            return method(other)
        return False

    def __ne__(self, other):
        method = self._get_mock_or_super('__ne__', create_if_missing=False)
        if method is not None:
            return method(other)
        return True

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
        return self._get_mock_or_super('__truediv__',
                                       aliases=['__div__'])(other)

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
        return self._get_mock_or_super('__rtruediv__',
                                       aliases=['__rdiv__'])(other)

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
        return self._get_mock_or_super('__itruediv__',
                                       aliases=['__idiv__'])(other)

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
        d = self.__dict__
        if '__dir__' in d:
            return d['__dir__']()

        def is_built_in(k):
            # TODO: replace hardcoded list from below with something more reliable
            return k.startswith('_BaseMock') or\
                k.startswith('__m_') or\
                k.startswith('_m_')

        return [k for k in d if not is_built_in(k)]

    def __sizeof__(self):
        return self._get_mock_or_super('__sizeof__')()

    def __getattr__(self, name):
        d = self.__dict__
        if '__getattr__' in d:
            return d['__getattr__'](name)
        d[name] = tmp = self.__make_leaf_node(name)
        return tmp

    def __make_leaf_node(self, name):
        max_depth = self._m_max_depth
        if max_depth < 0:
            return Mock(name, max_depth=self._m_max_depth, parent=self)
        if max_depth == 0:
            return FunctionMock(name, parent=self)
        return Mock(name, max_depth=max_depth - 1, parent=self)

    def __setattr__(self, name, value):
        return self._get_mock_or_super('__setattr__')(name, value)

    def __delattr__(self, name):
        return self._get_mock_or_super('__delattr__')(name)

    def __len__(self):
        method = self._get_mock_or_super('__len__', create_if_missing=False)
        if method is None:
            return NotImplemented
        return method()

    def __getitem__(self, name):
        d = self.__dict__
        if '__getitem__' in d:
            return d['__getitem__'](name)
        return d.get('__m_items', {})[name]

    def __setitem__(self, name, value):
        d = self.__dict__
        if '__setitem__' in d:
            d['__setitem__'](name, value)
        else:
            d.setdefault('__m_items', {})[name] = value

    def __delitem__(self, name):
        d = self.__dict__
        if '__delitem__' in d:
            d['__delitem__'](name)
        else:
            del d.get('__m_items', {})[name]

    def __reversed__(self):
        return self._get_mock_or_super('__reversed__')()

    def __contains__(self, key):
        return self._get_mock_or_super('__contains__')(key)

    def __iter__(self):
        method = self._get_mock_or_super('__iter__', create_if_missing=False)
        if method is not None:
            return method()
        return NotImplemented

    def __next__(self):
        return self._get_mock_or_super('__next__')()

    def __aiter__(self):
        return self._get_mock_or_super('__aiter__')()

    async def __anext__(self):
        return self._get_mock_or_super('__anext__')()

    def __enter__(self):
        method = self._get_mock_or_super('__enter__', create_if_missing=False)
        if method is not None:
            return method()
        return self

    async def __aenter__(self):
        method = self._get_mock_or_super('__aenter__', create_if_missing=False)
        if method is not None:
            return method()
        return self

    def __exit__(self, exc_type, exc, tb):
        method = self._get_mock_or_super('__exit__', create_if_missing=False)
        if method is None:
            return False
        return method(exc_type, exc, tb)

    async def __aexit__(self, exc_type, exc, tb):
        method = self._get_mock_or_super('__aexit__', create_if_missing=False)
        if method is None:
            return False
        return method(exc_type, exc, tb)

    def __get__(self, obj, obj_type):
        return self._get_mock_or_super('__get__')(obj, obj_type)

    def __set__(self, obj, value):
        return self._get_mock_or_super('__set__')(obj, value)

    def __delete__(self, obj):
        return self._get_mock_or_super('__delete__')(obj)

    def __m_children__(self):
        for item in self.__dict__.values():
            if isinstance(item, IMock):
                yield item

    def expect_call(self, *args, **kwargs):
        d = self.__dict__
        if 'expect_call' in d:
            return d['expect_call'](*args, **kwargs)
        return super().expect_call(*args, **kwargs)

    @_register_builtin_mock('expect_call')
    class _ExpectCallMock(BaseFunctionMock):

        def __call__(self, *args, **kwargs):
            fullname = self.__m_fullname__
            query = _utils.IterableQuery(self.__m_session__.expectations())
            if query.exists(lambda x: x.expected_call.name == fullname):
                return self.__m_call__(*args, **kwargs)
            return self.__m_parent__.__m_expect_call__(*args, **kwargs)

        def expect_call(self, *args, **kwargs):
            return self.__m_expect_call__(*args, **kwargs)

    @_register_builtin_mock('__get__')
    class _GetDescriptorMock(BaseFunctionMock):

        def __call__(self, obj, obj_type):
            return self.__m_call__(obj, obj_type)

        def expect_call(self, obj, obj_type):
            return self.__m_expect_call__(obj, obj_type)

    @_register_builtin_mock('__set__')
    class _SetDescriptorMock(BaseFunctionMock):

        def __call__(self, obj, value):
            return self.__m_call__(obj, value)

        def expect_call(self, obj, value):
            return self.__m_expect_call__(obj, value)

    @_register_builtin_mock('__delete__')
    class _DelDescriptorMock(BaseFunctionMock):

        def __call__(self, obj):
            return self.__m_call__(obj)

        def expect_call(self, obj):
            return self.__m_expect_call__(obj)

    @_register_builtin_mock('__getattr__')
    @_register_builtin_mock('__delattr__')
    class _GetDelAttrMock(BaseFunctionMock):

        def __call__(self, name):
            return self.__m_call__(name)

        def expect_call(self, name):
            parent_dict = self.__m_parent__.__dict__
            if name in parent_dict:
                del parent_dict[name]
            return self.__m_expect_call__(name)

    @_register_builtin_mock('__getitem__')
    @_register_builtin_mock('__delitem__')
    @_register_builtin_mock('__contains__')
    class _GetDelContainsItemMock(BaseFunctionMock):

        def __call__(self, key):
            return self.__m_call__(key)

        def expect_call(self, key):
            return self.__m_expect_call__(key)

    @_register_builtin_mock('__setattr__')
    class _SetAttrMock(BaseFunctionMock):

        def __call__(self, name, value):
            return self.__m_call__(name, value)

        def expect_call(self, name, value):
            return self.__m_expect_call__(name, value)

    @_register_builtin_mock('__setitem__')
    class _SetItemMock(BaseFunctionMock):

        def __call__(self, key, value):
            return self.__m_call__(key, value)

        def expect_call(self, key, value):
            return self.__m_expect_call__(key, value)

    @_register_builtin_mock('__iter__')
    @_register_builtin_mock('__next__')
    @_register_builtin_mock('__aiter__')
    @_register_builtin_mock('__anext__')
    @_register_builtin_mock('__enter__')
    @_register_builtin_mock('__aenter__')
    @_register_builtin_mock('__str__')
    @_register_builtin_mock('__repr__')
    @_register_builtin_mock('__hash__')
    @_register_builtin_mock('__sizeof__')
    @_register_builtin_mock('__int__')
    @_register_builtin_mock('__float__')
    @_register_builtin_mock('__complex__')
    @_register_builtin_mock('__bool__')
    @_register_builtin_mock('__index__')
    @_register_builtin_mock('__dir__')
    @_register_builtin_mock('__len__')
    @_register_builtin_mock('__reversed__')
    class _NoArgMethodMock(BaseFunctionMock):

        def __call__(self):
            return self.__m_call__()

        def expect_call(self):
            return self.__m_expect_call__()

    @_register_builtin_mock('__eq__')
    @_register_builtin_mock('__ne__')
    @_register_builtin_mock('__lt__')
    @_register_builtin_mock('__gt__')
    @_register_builtin_mock('__le__')
    @_register_builtin_mock('__ge__')
    @_register_builtin_mock('__add__')
    @_register_builtin_mock('__sub__')
    @_register_builtin_mock('__mul__')
    @_register_builtin_mock('__floordiv__')
    @_register_builtin_mock('__div__')
    @_register_builtin_mock('__truediv__')
    @_register_builtin_mock('__mod__')
    @_register_builtin_mock('__divmod__')
    @_register_builtin_mock('__pow__')
    @_register_builtin_mock('__lshift__')
    @_register_builtin_mock('__rshift__')
    @_register_builtin_mock('__and__')
    @_register_builtin_mock('__or__')
    @_register_builtin_mock('__xor__')
    @_register_builtin_mock('__radd__')
    @_register_builtin_mock('__rsub__')
    @_register_builtin_mock('__rmul__')
    @_register_builtin_mock('__rfloordiv__')
    @_register_builtin_mock('__rdiv__')
    @_register_builtin_mock('__rtruediv__')
    @_register_builtin_mock('__rmod__')
    @_register_builtin_mock('__rdivmod__')
    @_register_builtin_mock('__rpow__')
    @_register_builtin_mock('__rlshift__')
    @_register_builtin_mock('__rrshift__')
    @_register_builtin_mock('__rand__')
    @_register_builtin_mock('__ror__')
    @_register_builtin_mock('__rxor__')
    @_register_builtin_mock('__iadd__')
    @_register_builtin_mock('__isub__')
    @_register_builtin_mock('__imul__')
    @_register_builtin_mock('__ifloordiv__')
    @_register_builtin_mock('__idiv__')
    @_register_builtin_mock('__itruediv__')
    @_register_builtin_mock('__imod__')
    @_register_builtin_mock('__ipow__')
    @_register_builtin_mock('__ilshift__')
    @_register_builtin_mock('__irshift__')
    @_register_builtin_mock('__iand__')
    @_register_builtin_mock('__ior__')
    @_register_builtin_mock('__ixor__')
    class _BinaryOperatorMock(BaseFunctionMock):

        def __call__(self, other):
            return self.__m_call__(other)

        def expect_call(self, other):
            return self.__m_expect_call__(other)

    @_register_builtin_mock('__pos__')
    @_register_builtin_mock('__neg__')
    @_register_builtin_mock('__abs__')
    @_register_builtin_mock('__invert__')
    @_register_builtin_mock('__floor__')
    @_register_builtin_mock('__ceil__')
    @_register_builtin_mock('__trunc__')
    class _UnaryOperatorMock(BaseFunctionMock):

        def __call__(self):
            return self.__m_call__()

        def expect_call(self):
            return self.__m_expect_call__()

    @_register_builtin_mock('__round__')
    class _RoundOperatorMock(BaseFunctionMock):

        def __call__(self, ndigits=None):
            return self.__m_call__(ndigits=ndigits)

        def expect_call(self, ndigits=None):
            return self.__m_expect_call__(ndigits=ndigits)

    @_register_builtin_mock('__format__')
    class _FormatMock(BaseFunctionMock):

        def __call__(self, formatstr):
            return self.__m_call__(formatstr)

        def expect_call(self, formatstr):
            return self.__m_expect_call__(formatstr)

    @_register_builtin_mock('__call__')
    class _CallMock(BaseMock):

        def __m_children__(self):
            return
            yield

        def __m_expectations__(self):
            return
            yield

        def __call__(self, *args, **kwargs):
            return self.__m_parent__.__call__(*args, **kwargs)

        def expect_call(self, *args, **kwargs):
            return self.__m_parent__.expect_call(*args, **kwargs)

    @_register_builtin_mock('__exit__')
    @_register_builtin_mock('__aexit__')
    class _ContextExitMock(BaseFunctionMock):

        def __call__(self, exc_type, exc, tb):
            return self.__m_call__(exc_type, exc, tb)

        def expect_call(self, exc_type, exc, tb):
            return self.__m_expect_call__(exc_type, exc, tb)
