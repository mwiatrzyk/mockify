# ---------------------------------------------------------------------------
# mockify/mock.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import weakref
import itertools

from . import _utils
from ._engine import Call, Session
from .matchers import _


class _ChildMock:
    _mocked_properties = {
        '__getattr__': lambda: _GetAttrMock,
        '__setattr__': lambda: _SetAttrMock,
        'expect_call': lambda: _ExpectCallMock,
    }

    def __init__(self, name, session, parent):
        _utils.validate_mock_name(name)
        self._name = name
        self._session = session
        self._parent = parent

    def __repr__(self):
        return f"<{self.__module__}.{self.__class__.__name__}({self._fullname!r})>"

    def __setattr__(self, name, value):
        if '__setattr__' in self.__dict__:
            return self.__dict__['__setattr__'](name, value)
        else:
            return super().__setattr__(name, value)

    def __getattr__(self, name):
        if '__getattr__' in self.__dict__ :
            return self.__dict__['__getattr__'](name)
        else:
            self.__dict__[name] = tmp = _ChildMock(name, self._session, self)
            return tmp

    def __getattribute__(self, name):
        if name == '_mocked_properties':
            return super().__getattribute__(name)
        elif name not in self._mocked_properties:
            return super().__getattribute__(name)
        elif name in self.__dict__:
            return self.__dict__[name]
        else:
            mock_class = self._mocked_properties[name]()
            self.__dict__[name] = tmp = mock_class(self._session, self)
            return tmp

    def __call__(self, *args, **kwargs):
        actual_call = Call(self._fullname, *args, **kwargs)
        return self._session(actual_call)

    def expect_call(self, *args, **kwargs):
        expected_call = Call(self._fullname, *args, **kwargs)
        return self._session.expect_call(expected_call)

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

    @property
    def _fullname(self):
        parent = self._parent
        if parent is None:
            return self._name
        else:
            return f"{parent._fullname}.{self._name}"

    def _children(self):
        for obj in self.__dict__.values():
            if isinstance(obj, _ChildMock):
                yield obj

    def _expectations(self):
        return filter(
            lambda x: x.expected_call.name == self._fullname,
            self._session.expectations())


class _GetAttrMock(_ChildMock):
    _mocked_properties = {}

    def __init__(self, session, parent):
        super().__init__('__getattr__', session, parent)

    def __call__(self, name):
        actual_call = Call(self._fullname, name)
        return self._session(actual_call)

    def expect_call(self, name):
        if not _utils.is_identifier(name):
            raise TypeError(f"__getattr__.expect_call() must be called with valid Python property name, got {name!r}")
        if name in self._parent.__dict__:
            raise TypeError(
                f"__getattr__.expect_call() must be called with a non existing property name, "
                f"got {name!r} which already exists")
        expected_call = Call(self._fullname, name)
        return self._session.expect_call(expected_call)


class _SetAttrMock(_ChildMock):
    _mocked_properties = {}

    def __init__(self, session, parent):
        super().__init__('__setattr__', session, parent)

    def __call__(self, name, value):
        actual_call = Call(self._fullname, name, value)
        return self._session(actual_call)

    def expect_call(self, name, value):
        if not _utils.is_identifier(name):
            raise TypeError(f"__setattr__.expect_call() must be called with valid Python property name, got {name!r}")
        if name in self._parent.__dict__:
            raise TypeError(
                f"__setattr__.expect_call() must be called with a non existing property name, "
                f"got {name!r} which already exists")
        expected_call = Call(self._fullname, name, value)
        return self._session.expect_call(expected_call)


class _ExpectCallMock(_ChildMock):

    def __init__(self, session, parent):
        super().__init__('expect_call', session, parent)

    def __call__(self, *args, **kwargs):
        query = _utils.IterableQuery(self._session.expectations())
        if query.exists(lambda x: x.expected_call.name == self._fullname):
            return self._call(*args, **kwargs)
        else:
            return self._expect_call(*args, **kwargs)

    def _call(self, *args, **kwargs):
        actual_call = Call(self._fullname, *args, **kwargs)
        return self._session(actual_call)

    def _expect_call(self, *args, **kwargs):
        expected_call = Call(self._parent._fullname, *args, **kwargs)
        return self._session.expect_call(expected_call)


class MockInfo:
    """An object used to inspect given target mock.

    This class provides a sort of public interface on top of underlying
    :class:`Mock` instance, that due to its specific features has no methods
    or properties publicly available.

    :param mock:
        Instance of :class:`Mock` object to be inspected
    """

    def __init__(self, mock):
        self._mock = mock

    def __repr__(self):
        return f"<{self.__module__}.{self.__class__.__name__}({self._mock!r})>"

    @property
    def mock(self):
        """Reference to target mock object."""
        return self._mock

    @property
    def name(self):
        """Name of target mock."""
        return self._mock._fullname

    @property
    def session(self):
        """Instance of :class:`mockify.Session` assigned to given target mock."""
        return self._mock._session

    def expectations(self):
        """An iterator over all :class:`mockify.Expectation` objects recorded
        for target mock."""
        return self._mock._expectations()

    def children(self):
        """An iterator over target mock's direct children.

        It yields :class:`MockInfo` object for each target mock's
        children.
        """
        for child in self._mock._children():
            yield self.__class__(child)

    def walk(self):
        """Recursively iterates in depth-first order over all target mock's
        children and yields :class:`MockInfo` object for each found child.

        It always yields *self* as first element.
        """

        def walk(mock_info):
            yield mock_info
            for child_info in mock_info.children():
                yield from walk(child_info)

        yield from walk(self)


class MockFactory:
    """A factory class used to create groups of related mocks.

    This class allows to create mocks using class given by *mock_class*
    ensuring that:

    * names of created mocks are **unique**,
    * all mocks share one common session object.

    Instances of this class keep track of created mocks. Moreover, functions
    that would accept :class:`Mock` instances will also accept
    :class:`MockFactory` instances, so you can later f.e. check if all
    created mocks are satisfied using just a factory object. That makes it
    easy to manage multiple mocks in large test suites.

    See :ref:`managing-multiple-mocks` for more details.

    .. versionadded:: 1.0

    :param name:
        This is optional.

        Name of this factory to be used as a common prefix for all created
        mocks and nested factories.

    :param session:
        Instance of :class:`mockify.Session` to be used.

        If not given, a default session will be created and shared across all
        mocks created by this factory.

    :param mock_class:
        The class that will be used by this factory to create mocks.

        By default it will use :class:`Mock` class.
    """

    def __init__(self, name=None, session=None, mock_class=None):
        self._name = name
        self._session = session or Session()
        self._mock_class = mock_class or Mock
        self._factories = {}
        self._mocks = {}

    def mock(self, name):
        """Create and return mock of given *name*.

        This method will raise :exc:`TypeError` if *name* is already used by
        either mock or child factory.
        """
        self._validate_name(name)
        self._mocks[name] = tmp =\
            self._mock_class(self._format_name(name), session=self._session)
        return tmp

    def factory(self, name):
        """Create and return child factory.

        Child factory will use session from its parent, and will prefix all
        mocks and grandchild factories with given *name*.

        This method will raise :exc:`TypeError` if *name* is already used by
        either mock or child factory.

        :rtype: MockFactory
        """
        self._validate_name(name)
        self._factories[name] = tmp = self.__class__(
            self._format_name(name),
            session=self._session,
            mock_class=self._mock_class)
        return tmp

    def _validate_name(self, name):
        if name in self._mocks or name in self._factories:
            raise TypeError(f"Name {name!r} is already in use")

    def _format_name(self, name):
        if self._name is None:
            return name
        else:
            return f"{self._name}.{name}"

    def _children(self):
        yield from self._mocks.values()
        for child_factory in self._factories.values():
            yield from child_factory._children()

    def _expectations(self):
        for mock in self._children():
            yield from mock._expectations()


class Mock(_ChildMock):
    """All-in-one mocking utility.

    This class is used to:

    * create mocks of functions,
    * create mocks of objects with methods, setters and getters,
    * create mocks of modules,
    * create ad-hoc data objects.

    No matter what you will be mocking, for all cases creating mock objects
    is always the same - by giving it a *name* and optionally *session*. Mock
    objects automatically create attributes on demand, and that attributes
    form some kind of **nested** or **child** mocks.

    To record expectations, you have to call **expect_call()** method on one
    of that attributes, or on mock object itself (for function mocks). Then
    you pass mock object to unit under test. Finally, you will need
    :func:`mockify.assert_satisfied` function or :func:`mockify.satisfied`
    context manager to check if the mock is satisfied.

    Here's an example:

    .. testcode::

        from mockify import satisfied
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

    .. versionadded:: 1.0
    """

    def __init__(self, name, session=None):
        super().__init__(name, session or Session(), None)
