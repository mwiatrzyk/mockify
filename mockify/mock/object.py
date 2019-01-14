from mockify.engine import Registry
from mockify.mock.function import Function


class Object:
    """Mock frontend made for mocking Python objects.

    This class requires custom subclass to be created and have following
    attributes defined:

        __methods__
            Containing list of method names

        __properties__
            Containing list of property names

    For example, if you want to mock Python class that has methods ``foo`` and
    ``bar``, and propety ``spam``, you would create following subclass::

        >>> class Mock(Object):
        ...     __methods__ = ['foo', 'bar']
        ...     __properties__ = ['spam']

    After that, class ``Mock`` can be instantiated like this::

        >>> mock = Mock('mock')

    And then injected to some unit under test.

    :param name:
        Name of this object mock instance

    :param registry:
        This parameter is optional.

        If you omit it, new instance of :class:`mockify.engine.Registry` will
        be created and used by this object mock. This is useful if you already
        have registry instance that you want to share between many unrelated
        mock frontends.
    """
    __methods__ = None
    __properties__ = None

    class _Property:

        def __init__(self, name, registry):
            self._fset = Function(name + '.fset', registry=registry)
            self._fget = Function(name + '.fget', registry=registry)

        @property
        def fset(self):
            return self._fset

        @property
        def fget(self):
            return self._fget

    def __init__(self, name, registry=None):
        if not self.__methods__ or not self.__properties__:
            raise TypeError("missing '__methods__' and/or '__properties__' attributes in class definition")
        self._name = name
        self._registry = registry or Registry()
        self._methods = dict(self.__create_methods(self.__methods__))
        self._properties = dict(self.__create_properties(self.__properties__))

    def __create_methods(self, names):
        for name in names:
            yield name, Function("{}.{}".format(self._name, name), self._registry)

    def __create_properties(self, names):
        for name in names:
            yield name, self._Property("{}.{}".format(self._name, name), self._registry)

    def __getattr__(self, name):
        if name in self._methods:
            return self._methods[name]
        elif name in self._properties:
            return self._properties[name].fget()
        else:
            raise AttributeError(
                "mock object {!r} has no attribute named {!r}".
                format(self._name, name))

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
        elif name in self._properties:
            self._properties[name].fset(value)
        else:
            raise AttributeError("mock object {!r} has no property {!r}".format(self._name, name))

    def expect_call(self, _name_, *args, **kwargs):
        """Record method call expectation.

        This method requires one argument to be given - method name. All other
        are simply forwarded to underlying
        :class:`mockify.mock.function.Function` object.

        :param _name_:
            Method name
        """
        return self._methods[_name_].expect_call(*args, **kwargs)

    def expect_set(self, name, value):
        """Record property set expectation.

        :param name:
            Property name
        :param value:
            Property value that is expected to be set.
        """
        return self._properties[name].fset.expect_call(value)

    def expect_get(self, name):
        """Record property get expectation.

        :param name:
            Property name
        """
        return self._properties[name].fget.expect_call()

    def assert_satisfied(self):
        """Check if this mock object is satisfied.

        This method checks (in one call) if all registered expectations (for
        all methods and all properties) are satisfied. If not, then
        :exc:`mockify.exc.Unsatisfied` exception is raised.
        """
        self._registry.assert_satisfied()
