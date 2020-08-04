import abc
import inspect
import weakref

from .. import _utils


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
        Abstract sase class to be implemented by this mock.

        This must be subclass of :class:`abc.ABC`

    :param session:
        Instance of :class:`mockify.Session` to be used for this mock.

        Default one will automatically be used if left empty.

    .. versionadded:: 0.8
    """
    _unset = object()

    def __new__(cls, name, abstract_base_class, session=None):
        if not isinstance(abstract_base_class, type):
            cls.__raise_invalid_abstract_base_class_error('{!r} instance', type(abstract_base_class))
        if not issubclass(abstract_base_class, abc.ABC):
            cls.__raise_invalid_abstract_base_class_error('{!r} class', abstract_base_class)

        class Mock(abstract_base_class):

            class _Proxy:

                def __init__(self, owner):
                    self._owner = owner

                @property
                def _owner(self):
                    return self.__owner()

                @_owner.setter
                def _owner(self, value):
                    self.__owner = weakref.ref(value)

            class _GetAttrProxy(_Proxy):

                def expect_call(self, name):
                    raise AttributeError(
                        "{self._owner.__class__.__name__!r} object has no "
                        "attribute {name!r}".format(self=self, name=name))

            class _SetAttrProxy(_Proxy):

                def expect_call(self, name, value):
                    raise AttributeError("cannot set attribute {!r} (it is missing in the interface)".format(name))

            class _MethodProxy(_Proxy):

                def __init__(self, owner, method_name):
                    super().__init__(owner)
                    self._method_name = method_name

                def expect_call(self, *args, **kwargs):
                    expected_signature = str(self._owner._abstract_methods[self._method_name]).\
                        replace('self, ', '').\
                        replace('self', '')  # FIXME: this is a workaround
                    call_signature = _utils.format_args_kwargs(args, kwargs)
                    raise TypeError(
                        "cannot record call expectation due to signature mismatch: "
                        "{name}.{method}{expected_signature} (expected) != {name}.{method}({given_signature}) (given)".format(
                            name=self._owner._name, method=self._method_name, expected_signature=expected_signature,
                            given_signature=call_signature))

            def __init__(self, name, abstract_methods, abstract_properties, session):
                self._name = name
                self._abstract_methods = abstract_methods
                self._abstract_properties = abstract_properties
                self.__m_session__ = session

            def __getattribute__(self, name):
                if name in ('_abstract_methods',):
                    return super().__getattribute__(name)
                elif name == '__getattr__':
                    return self._GetAttrProxy(self)
                elif name == '__setattr__':
                    return self._SetAttrProxy(self)
                elif name in self._abstract_methods:
                    return self._MethodProxy(self, name)
                else:
                    return super().__getattribute__(name)

        abstract_methods = {}
        abstract_properties = set()
        for method_name in Mock.__abstractmethods__:
            attr = getattr(abstract_base_class, method_name)
            if isinstance(attr, property):
                abstract_properties.add(method_name)
            else:
                abstract_methods[method_name] = inspect.signature(attr)

        Mock.__abstractmethods__ = frozenset()
        Mock.__name__ = cls.__name__
        return Mock(name, abstract_methods, abstract_properties, session)

    @classmethod
    def __raise_invalid_abstract_base_class_error(cls, message, *args):
        message = message.format(*args)
        raise TypeError(
            "'__init__' got an invalid value for argument 'abstract_base_class': "
            "ABC subclass expected, got {}".format(message))
