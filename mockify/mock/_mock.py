# ---------------------------------------------------------------------------
# mockify/mock/_mock.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
from ._base import BaseMock
from .._engine import Session, Call
from .. import _utils


class _BaseMock(BaseMock):
    _mocked_properties = {
        '__getattr__': lambda: _GetAttrMock,
        '__setattr__': lambda: _SetAttrMock,
        'expect_call': lambda: _ExpectCallMock,
    }

    def __init__(self, name, session, parent=None):
        _utils.validate_mock_name(name)
        self.__name = name
        self.__session = session
        self.__m_parent__ = parent

    @property
    def __m_name__(self):
        return self.__name

    @property
    def __m_session__(self):
        return self.__session

    def __m_children__(self):
        for obj in self.__dict__.values():
            if isinstance(obj, _BaseMock):
                yield obj

    def __m_expectations__(self):
        fullname = self.__m_fullname__
        return filter(
            lambda x: x.expected_call.name == fullname,
            self.__m_session__.expectations())

    def __setattr__(self, name, value):
        if '__setattr__' in self.__dict__:
            return self.__dict__['__setattr__'](name, value)
        else:
            return super().__setattr__(name, value)

    def __getattr__(self, name):
        if '__getattr__' in self.__dict__ :
            return self.__dict__['__getattr__'](name)
        else:
            self.__dict__[name] = tmp = _BaseMock(name, self.__m_session__, self)
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
            self.__dict__[name] = tmp = mock_class(self.__m_session__, self)
            return tmp

    def __call__(self, *args, **kwargs):
        actual_call = Call(self.__m_fullname__, *args, **kwargs)
        return self.__m_session__(actual_call)

    def expect_call(self, *args, **kwargs):
        expected_call = Call(self.__m_fullname__, *args, **kwargs)
        return self.__m_session__.expect_call(expected_call)


class _GetAttrMock(_BaseMock):
    _mocked_properties = {}

    def __init__(self, session, parent):
        super().__init__('__getattr__', session, parent)

    def __call__(self, name):
        actual_call = Call(self.__m_fullname__, name)
        return self.__m_session__(actual_call)

    def expect_call(self, name):
        if not _utils.is_identifier(name):
            raise TypeError("__getattr__.expect_call() must be called with valid Python property name, got {!r}".format(name))
        if name in self.__m_parent__.__dict__:
            raise TypeError(
                "__getattr__.expect_call() must be called with a non existing property name, "
                "got {!r} which already exists".format(name))
        expected_call = Call(self.__m_fullname__, name)
        return self.__m_session__.expect_call(expected_call)


class _SetAttrMock(_BaseMock):
    _mocked_properties = {}

    def __init__(self, session, parent):
        super().__init__('__setattr__', session, parent)

    def __call__(self, name, value):
        actual_call = Call(self.__m_fullname__, name, value)
        return self.__m_session__(actual_call)

    def expect_call(self, name, value):
        if not _utils.is_identifier(name):
            raise TypeError("__setattr__.expect_call() must be called with valid Python property name, got {!r}".format(name))
        if name in self.__m_parent__.__dict__:
            raise TypeError(
                "__setattr__.expect_call() must be called with a non existing property name, "
                "got {!r} which already exists".format(name))
        expected_call = Call(self.__m_fullname__, name, value)
        return self.__m_session__.expect_call(expected_call)


class _ExpectCallMock(_BaseMock):

    def __init__(self, session, parent):
        super().__init__('expect_call', session, parent)

    def __call__(self, *args, **kwargs):
        query = _utils.IterableQuery(self.__m_session__.expectations())
        if query.exists(lambda x: x.expected_call.name == self.__m_fullname__):
            return self._call(*args, **kwargs)
        else:
            return self._expect_call(*args, **kwargs)

    def _call(self, *args, **kwargs):
        actual_call = Call(self.__m_fullname__, *args, **kwargs)
        return self.__m_session__(actual_call)

    def _expect_call(self, *args, **kwargs):
        expected_call = Call(self.__m_parent__.__m_fullname__, *args, **kwargs)
        return self.__m_session__.expect_call(expected_call)


class Mock(_BaseMock):
    """General purpose mock class.

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

    .. versionchanged:: 0.8
        Now this class inherits from :class:`mockify.mock.BaseMock`

    .. versionadded:: 0.6
    """

    def __init__(self, name, session=None):
        super().__init__(name, session or Session(), None)


