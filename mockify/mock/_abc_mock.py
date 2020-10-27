# ---------------------------------------------------------------------------
# mockify/mock/_abc_mock.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import abc
import inspect
import weakref

from ._base import BaseMock
from .. import _utils
from .._engine import Call, Session
from ._function import FunctionMock


class ABCMock:
    """Mock class for creating mocks that implement given :class:`abc.ABC`
    subclass.

    This class is meant to be used with interfaces containing abstract
    methods. It performs a lookup on the interface and allows to record
    expectations only on methods that are defined in the interface. Moreover,
    it also checks argument names and disallow recording calls with invalid
    arguments; everything must match the definition of the interface.

    Here's an example:

    .. testcode::

        import abc

        from mockify import satisfied
        from mockify.mock import ABCMock
        from mockify.actions import Return

        class Interface(abc.ABC):

            @abc.abstractmethod
            def method(self, a, b):
                pass

        mock = ABCMock('mock', Interface)
        mock.method.expect_call(1, 2).will_once(Return(123))
        with satisfied(mock):
            assert mock.method(1, 2) == 123

    :param name:
        Mock name

    :param abstract_base_class:
        Subclass of :class:`abc.ABC` to be used as source of abstract methods
        that will be implemented by this mock.

    .. versionchanged:: 0.9
        Parameter ``session`` is removed in favour of ``**kwargs``; session
        is now handled by :class:`BaseMock` class

    .. versionadded:: 0.8
    """
    _unset = object()

    def __new__(cls, name, abstract_base_class, **kwargs):
        if not isinstance(abstract_base_class, type) or\
           not issubclass(abstract_base_class, abc.ABC):
            raise TypeError("__init__() got an invalid value for argument 'abstract_base_class'")

        class InnerMock(BaseMock):
            __abstract_methods__ = {}
            __abstract_properties__ = set()

            class _Proxy(BaseMock):

                def __init__(self, name, parent):
                    super().__init__(name=name, parent=parent)
                    self._mock = FunctionMock(name, parent=parent)

                def __m_children__(self):
                    return iter([])

                def __m_expectations__(self):
                    yield from self._mock.__m_expectations__()

            class _GetAttrProxy(_Proxy):

                def __call__(self, name):
                    return self._mock(name)

                def expect_call(self, name):
                    if name not in self.__m_parent__.__abstract_properties__:
                        raise AttributeError("{self.__m_parent__.__class__.__name__!r} object has no attribute {name!r}".format(self=self, name=name))
                    return self._mock.expect_call(name)

            class _SetAttrProxy(_Proxy):

                def __call__(self, name, value):
                    return self._mock(name, value)

                def expect_call(self, name, value):
                    if name not in self.__m_parent__.__abstract_properties__:
                        raise AttributeError("can't set attribute {name!r} (not defined in the interface)".format(name=name))
                    return self._mock.expect_call(name, value)

            class _MethodProxy(_Proxy):

                def __init__(self, name, signature, parent):
                    super().__init__(name, parent)
                    self.__signature = signature

                def __call__(self, *args, **kwargs):
                    self._validate_signature(*args, **kwargs)
                    return self._mock(*args, **kwargs)

                def expect_call(self, *args, **kwargs):
                    self._validate_signature(*args, **kwargs)
                    return self._mock.expect_call(*args, **kwargs)

                def _validate_signature(self, *args, **kwargs):
                    expected_signature = self.__signature
                    expected_signature_str = str(expected_signature).\
                        replace('self, ', '').\
                        replace('self', '')  # Drop self from error print
                    try:
                        expected_signature.bind(self, *args, **kwargs)
                    except TypeError as e:
                        raise TypeError("{self.__m_parent__.__m_name__}.{self.__m_name__}{sig}: {err}".format(sig=expected_signature_str, err=e, self=self))

            def __init__(self, name, **kwargs):
                super().__init__(name=name, **kwargs)
                if self.__abstract_properties__:
                    self.__dict__['__getattr__'] = self._GetAttrProxy('__getattr__', self)
                    self.__dict__['__setattr__'] = self._SetAttrProxy('__setattr__', self)
                for name, signature in self.__abstract_methods__.items():
                    self.__dict__[name] = self._MethodProxy(name, signature, self)

            def __setattr__(self, name, value):
                if name.startswith('_'):
                    super().__setattr__(name, value)
                elif name in self.__abstract_properties__:
                    self.__dict__['__setattr__'](name, value)
                else:
                    raise AttributeError("can't set attribute {!r} (not defined in the interface)".format(name))

            def __getattr__(self, name):
                if name in self.__abstract_properties__:
                    return self.__dict__['__getattr__'](name)
                else:
                    raise AttributeError("{!r} object has no attribute {!r}".format(self.__class__.__name__, name))

            def __m_children__(self):
                for obj in self.__dict__.values():
                    if isinstance(obj, self._Proxy):
                        yield obj

            def __m_expectations__(self):
                return iter([])

        abstract_base_class.register(InnerMock)
        for method_name in abstract_base_class.__abstractmethods__:
            method = getattr(abstract_base_class, method_name)
            if isinstance(method, property):
                InnerMock.__abstract_properties__.add(method_name)
            else:
                InnerMock.__abstract_methods__[method_name] = inspect.signature(method)
        InnerMock.__name__ = cls.__name__
        return InnerMock(name, **kwargs)

    @classmethod
    def _iter_abstract_methods(cls, abstract_base_class):
        for name in abstract_base_class.__abstractmethods__:
            yield getattr(abstract_base_class, name)
