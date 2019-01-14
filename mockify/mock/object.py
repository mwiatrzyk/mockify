from mockify.engine import Registry
from mockify.mock.function import Function


class Object:

    def __init__(self, name, methods=None, registry=None):
        self._name = name
        self._registry = registry or Registry()
        self._methods = dict(self.__create_methods(methods))

    def __create_methods(self, names):
        for name in names:
            yield name, Function("{}.{}".format(self._name, name), self._registry)

    def __getattr__(self, name):
        if name in self._methods:
            return self._methods[name]
        else:
            raise AttributeError(
                "{!r} mock object has no attribute named {!r}".
                format(self._name, name))

    @property
    def __methods__(self):
        return self._methods

    def assert_satisfied(self):
        self._registry.assert_satisfied()
