import abc
import inspect
import weakref

from ._base import BaseMock
from .. import _utils
from .._engine import Session
from ._mock import Mock


class ABCMock:
    """Mock class for creating mocks that implement given :class:`abc.ABC`
    subclass.

    This class is meant to be used with interfaces containing abstract
    methods. It performs a lookup on the interface and allows to record
    expectations only on methods that are defined in the interface. Moreover,
    it also checks argument names and disallow recording calls with invalid
    arguments; everything must match the definition of the interface.

    :param name:
        Mock name

    :param abstract_base_class:
        Subclass of :class:`abc.ABC` to be used as source of abstract methods
        that will be implemented by this mock.

    :param session:
        Instance of :class:`mockify.Session` to be used for this mock.

        Default one will automatically be used if left empty.

    .. versionadded:: 0.8
    """
    _unset = object()

    def __new__(cls, name, abstract_base_class, session=None):
        if not isinstance(abstract_base_class, type) or\
           not issubclass(abstract_base_class, abc.ABC):
            raise TypeError("__init__() got an invalid value for argument 'abstract_base_class'")

        class InnerMock(BaseMock):
            __abstract_methods__ = {}
            __abstract_properties__ = set()

            class _Proxy(BaseMock):

                def __init__(self, name, parent):
                    self.__name = name
                    self.__m_parent__ = parent
                    # TODO: Replace with a FunctionMock (to be added)
                    self._mock = Mock(self.__m_fullname__, session=parent.__m_session__)

                @property
                def __m_name__(self):
                    return self.__name

                @property
                def __m_session__(self):
                    return self.__m_parent__.__m_session__

                def __m_children__(self):
                    return
                    yield

                def __m_expectations__(self):
                    yield from self._mock.__m_expectations__()

            class _GetAttrProxy(_Proxy):

                def expect_call(self, name):
                    if name not in self.__m_parent__.__abstract_properties__:
                        raise AttributeError("{self.__m_parent__.__class__.__name__!r} object has no attribute {name!r}".format(self=self, name=name))

            class _SetAttrProxy(_Proxy):

                def expect_call(self, name, value):
                    if name not in self.__m_parent__.__abstract_properties__:
                        raise AttributeError("can't set attribute {name!r}".format(name=name))

            class _MethodProxy(_Proxy):

                def __call__(self, *args, **kwargs):
                    return self._mock(*args, **kwargs)

                def expect_call(self, *args, **kwargs):
                    expected_signature = self.__m_parent__.__abstract_methods__[self.__m_name__]
                    expected_signature_str = str(expected_signature).\
                        replace('self, ', '').\
                        replace('self', '')  # Drop self from error print
                    try:
                        expected_signature.bind(self, *args, **kwargs)
                    except TypeError as e:
                        raise TypeError("{self.__m_parent__.__m_name__}.{self.__m_name__}{sig}: {err}".format(sig=expected_signature_str, err=e, self=self))
                    else:
                        return self._mock.expect_call(*args, **kwargs)

            def __init__(self, name, session):
                self.__name = name
                self.__session = session
                self.__m_parent__ = None

            def __getattribute__(self, name):
                if name == '__dict__':
                    return super().__getattribute__(name)
                elif name in self.__dict__:
                    return self.__dict__[name]
                elif name == '__getattr__':
                    self.__dict__[name] = tmp = self.__class__._GetAttrProxy(name, self)
                    return tmp
                elif name == '__setattr__':
                    self.__dict__[name] = tmp =self.__class__._SetAttrProxy(name, self)
                    return tmp
                elif name.startswith('_'):
                    return super().__getattribute__(name)
                elif name not in self.__abstract_methods__:
                    raise AttributeError("{self.__class__.__name__!r} object has no attribute {name!r}".format(self=self, name=name))
                else:
                    self.__dict__[name] = tmp = self.__class__._MethodProxy(name, self)
                    return tmp

            @property
            def __m_name__(self):
                return self.__name

            @property
            def __m_session__(self):
                return self.__session

            def __m_children__(self):
                for obj in self.__dict__.values():
                    if isinstance(obj, self._Proxy):
                        yield obj

            def __m_expectations__(self):
                return
                yield

        abstract_base_class.register(InnerMock)
        for method_name in abstract_base_class.__abstractmethods__:
            method = getattr(abstract_base_class, method_name)
            if isinstance(method, property):
                InnerMock.__abstract_properties__.add(method_name)
            else:
                InnerMock.__abstract_methods__[method_name] = inspect.signature(method)
        InnerMock.__name__ = cls.__name__
        return InnerMock(name, session or Session())

    @classmethod
    def _iter_abstract_methods(cls, abstract_base_class):
        for name in abstract_base_class.__abstractmethods__:
            yield getattr(abstract_base_class, name)
