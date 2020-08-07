import abc
import inspect
import weakref

from ._base import BaseMock
from .. import _utils
from .._engine import Session


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

        class Mock(BaseMock):
            __abstract_methods__ = {}
            __abstract_properties__ = set()

            class _Proxy:

                def __init__(self, name, parent):
                    self._name = name
                    self._parent = parent

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

            class _GetAttrProxy(_Proxy):

                def expect_call(self, name):
                    if name not in self._parent.__abstract_properties__:
                        raise AttributeError("{self._parent.__class__.__name__!r} object has no attribute {name!r}".format(self=self, name=name))

            class _SetAttrProxy(_Proxy):

                def expect_call(self, name, value):
                    if name not in self._parent.__abstract_properties__:
                        raise AttributeError("can't set attribute {name!r}".format(name=name))

            class _MethodProxy(_Proxy):

                def expect_call(self, *args, **kwargs):
                    expected_signature = self._parent.__abstract_methods__[self._name]
                    expected_signature_str = str(expected_signature).\
                        replace('self, ', '').\
                        replace('self', '')  # Drop self from error print
                    try:
                        expected_signature.bind(self, *args, **kwargs)
                    except TypeError as e:
                        raise TypeError("{self._parent.__m_name__}.{self._name}{sig}: {err}".format(sig=expected_signature_str, err=e, self=self))

            def __init__(self, name, session):
                self.__name = name
                self.__session = session

            def __getattribute__(self, name):
                if name == '__getattr__':
                    return self.__class__._GetAttrProxy(name, self)
                elif name == '__setattr__':
                    return self.__class__._SetAttrProxy(name, self)
                elif name.startswith('_'):
                    return super().__getattribute__(name)
                elif name not in self.__abstract_methods__:
                    raise AttributeError("{self.__class__.__name__!r} object has no attribute {name!r}".format(self=self, name=name))
                else:
                    return self.__class__._MethodProxy(name, self)

            @property
            def __m_name__(self):
                return self.__name

            @property
            def __m_session__(self):
                return self.__session

            @property
            def __m_children__(self):
                return
                yield

            @property
            def __m_expectations__(self):
                return
                yield

        abstract_base_class.register(Mock)
        for method_name in abstract_base_class.__abstractmethods__:
            method = getattr(abstract_base_class, method_name)
            if isinstance(method, property):
                Mock.__abstract_properties__.add(method_name)
            else:
                Mock.__abstract_methods__[method_name] = inspect.signature(method)
        Mock.__name__ = cls.__name__
        return Mock(name, session or Session())

    @classmethod
    def _iter_abstract_methods(cls, abstract_base_class):
        for name in abstract_base_class.__abstractmethods__:
            yield getattr(abstract_base_class, name)
