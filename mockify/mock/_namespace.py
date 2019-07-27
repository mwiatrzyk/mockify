# ---------------------------------------------------------------------------
# mockify/mock/_module.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------

import contextlib
import itertools
import weakref

from mockify import Call, Registry, _utils, exc

from ._function import Function


class Namespace:
    """Used to mock functions that are behind some kind of a namespace.

    .. versionadded:: 0.5

    .. testsetup::

        from mockify.mock import Namespace
        from mockify.actions import Return

    Look at following code::

        if os.path.isfile(path):
            do_something_with_file(path)

    It is very common pattern of how :mod:`os` is used by Python
    applications. And basically :class:`Namespace` can be used to make it
    easier to mock such statements. You simply do it like this:

    .. testcode::

        os = Namespace('os')
        os.path.isfile.expect_call('/foo/bar/baz.txt').will_once(Return(True))

    And now you can call such mocked statement:

    .. testcode::

        assert os.path.isfile('/foo/bar/baz.txt')

    There is no namespace nesting limit.

    :param name:
        Mock name.

        This will be used as a prefix for all namespaced mocks created by
        this class.

    :param registry:
        Instance of :class:`mockify.Registry` to be used.

        If not given, a default one will be created for this mock object.

    :param mock_class:
        Mock class to be used for "leaf" nodes.

        By default, this is :class:`mockify.mock.Function`, but you can give
        any other mock class here.
    """

    class _Nested:

        def __init__(self, name, parent):
            self._name = name
            self._parent = parent
            self._nested = {}

        def __getattr__(self, name):
            if name not in self._nested:
                self._nested[name] = self.__class__(name, self)
            return self._nested[name]

        def __call__(self, *args, **kwargs):
            call = Call(self.name, args, kwargs)
            raise exc.UninterestedCall(call)

        @property
        def _parent(self):
            return self.__parent()

        @_parent.setter
        def _parent(self, value):
            self.__parent = weakref.ref(value)

        @property
        def _mock_class(self):
            return self._parent._mock_class

        @property
        def _registry(self):
            return self._parent._registry

        @property
        def _mocks(self):
            for value in self._nested.values():
                if isinstance(value, self._mock_class):
                    yield value
                else:
                    yield from value._mocks

        @property
        def name(self):
            return f"{self._parent.name}.{self._name}"

        def expect_call(self, *args, **kwargs):
            mock_class = self._mock_class
            parent_nested = self._parent._nested
            mocks = list(itertools.islice(self._mocks, 1))
            if mocks:
                raise TypeError(
                    f"Cannot record expectation: {self.name!r} is a subpath "
                    f"of another mock {mocks[0].name!r} registered earlier.")
            if not isinstance(parent_nested[self._name], mock_class):
                parent_nested[self._name] = mock_class(self.name, registry=self._registry)
            return parent_nested[self._name].expect_call(*args, **kwargs)

    def __init__(self, name, registry=None, mock_class=None):
        self._name = name
        self._registry = registry or Registry()
        self._mock_class = mock_class or Function
        self._nested = {}

    def __getattr__(self, name):
        if name not in self._nested:
            self._nested[name] = self._Nested(name, self)
        return self._nested[name]

    @property
    def _mocks(self):
        for value in self._nested.values():
            if isinstance(value, self._mock_class):
                yield value
            else:
                yield from value._mocks

    @contextlib.contextmanager
    def __patch_hook__(self):
        mocks = {m.name: m for m in self._mocks}
        with patch(mocks):
            yield

    @property
    def name(self):
        """Name of this namespace mock.

        This will be a root for all nested namespaces.
        """
        return self._name

    def assert_satisfied(self):
        """Check if all mocks created within this namespace are satisfied."""
        self._registry.assert_satisfied(*map(lambda x: x.name, self._mocks))
