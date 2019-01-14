from mockify.engine import Registry
from mockify.mock.function import Function


class Object:

    class _Property:

        def __init__(self, name, registry):
            self._fset = Function(name + '.fset', registry=registry)

        @property
        def fset(self):
            return self._fset

    def __init__(self, name, methods=None, properties=None, registry=None):
        self._name = name
        self._registry = registry or Registry()
        self._methods = dict(self.__create_methods(methods))
        self._properties = dict(self.__create_properties(properties))

    def __create_methods(self, names):
        for name in names:
            yield name, Function("{}.{}".format(self._name, name), self._registry)

    def __create_properties(self, names):
        for name in names:
            yield name, self._Property("{}.{}".format(self._name, name), self._registry)

    def __getattr__(self, name):
        if name in self._methods:
            return self._methods[name]
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

    @property
    def __methods__(self):
        return self._methods

    def expect_set(self, name, value):
        self._properties[name].fset.expect_call(value)

    def assert_satisfied(self):
        self._registry.assert_satisfied()
