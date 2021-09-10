# ---------------------------------------------------------------------------
# mockify/mock/_factory.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

from mockify import _utils

from ._base import BaseMock
from ._mock import Mock

__all__ = export = _utils.ExportList()  # pylint: disable=invalid-all-format


@export
class MockFactory(BaseMock):
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

    .. versionchanged:: 0.8
        Now it inherits from :class:`mockify.mock.BaseMock`, as this class is
        more or less special kind of mock.

    .. versionadded:: 0.6

    :param name:
        This is optional.

        Name of this factory to be used as a common prefix for all created
        mocks and nested factories.

    :param mock_class:
        The class that will be used by this factory to create mocks.

        By default it will use :class:`Mock` class.

    .. versionchanged:: 0.9
        Removed parameter ``session`` in favour of ``**kwargs``; session
        handling is now done by :class:`BaseMock` class.
    """

    def __init__(self, name=None, mock_class=None, **kwargs):
        super().__init__(name, **kwargs)
        self._mock_class = mock_class or Mock
        self._factories = {}
        self._mocks = {}

    def __m_children__(self):
        yield from self._mocks.values()
        yield from self._factories.values()

    def __m_expectations__(self):
        for mock in self._mocks.values():
            yield from mock.__m_expectations__()

    def __repr__(self):
        return "<{self.__module__}.{self.__class__.__name__}({self.__m_fullname__!r})>".format(
            self=self
        )

    def mock(self, name):
        """Create and return mock of given *name*.

        This method will raise :exc:`TypeError` if *name* is already used by
        either mock or child factory.
        """
        self._raise_if_name_is_in_use(name)
        self._mocks[name] = tmp = self._mock_class(name, parent=self)
        return tmp

    def factory(self, name):
        """Create and return child factory.

        Child factory will use session from its parent, and will prefix all
        mocks and grandchild factories with given *name*.

        This method will raise :exc:`TypeError` if *name* is already used by
        either mock or child factory.

        :rtype: MockFactory
        """
        self._raise_if_name_is_in_use(name)
        self._factories[name] = tmp =\
            self.__class__(
                name=name,
                mock_class=self._mock_class,
                parent=self)
        return tmp

    def _raise_if_name_is_in_use(self, name):
        if name in self._mocks or name in self._factories:
            raise TypeError("Name {!r} is already in use".format(name))
