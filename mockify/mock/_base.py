# ---------------------------------------------------------------------------
# mockify/mock/_base.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

# pylint: disable=missing-module-docstring

import typing

from mockify import _utils
from mockify.abc import IMock, ISession
from mockify.core._session import Session

__all__ = export = _utils.ExportList()  # pylint: disable=invalid-all-format


@export
class BaseMock(IMock):  # pylint: disable=too-few-public-methods
    """Base class for all mock classes.

    This class provides partial implementation of :class:`mockify.abc.IMock`
    interface and common constructor used by all mocks. If you need to create
    custom mock, then it is better to inherit from this class at first place, as
    it provides some basic initialization out of the box.

    :param name:
        Name of this mock.

        This will be returned by :attr:`__m_name__` property.

        See :attr:`mockify.abc.IMock.__m_name__` for more information about
        naming mocks.

    :param session:
        Instance of :class:`mockify.abc.ISession` to be used.

        If not given, parent's session will be used (if parent exist) or a
        default :class:`mockify.core.Session` session object will be created and
        used.

        .. note::
            This option is self-exclusive with *parent* parameter.

    :param parent:
        Instance of :class:`mockify.abc.IMock` representing parent for this
        mock.

        When this parameter is given, mock implicitly uses paren't session
        object.

        .. note::
            This option is self-exclusive with *session* parameter.

    .. versionchanged:: 0.13
        Moved from :mod:`mockify.core` into :mod:`mockify.mock`.

    .. versionchanged:: 0.9
        Added ``__init__`` method, as it is basically same for all mock
        classes.

    .. versionadded:: 0.8
    """

    def __init__(
        self, name: str, session: ISession = None, parent: IMock = None
    ):
        self.__name = name
        self.__parent = _utils.make_weak(parent)
        if name is not None:
            _utils.validate_mock_name(name)
        if session is not None and parent is not None:
            raise TypeError("cannot set both 'session' and 'parent'")
        if session is not None:
            self.__session = session
        elif parent is not None:
            self.__session = parent.__m_session__
        else:
            self.__session = Session()

    def __repr__(self):
        module = self.__module__
        if module.startswith('mockify.mock'):
            module = 'mockify.mock'  # Hide private submodule in repr()
        return "<{module}.{self.__class__.__qualname__}({self.__m_name__!r})>".format(
            module=module, self=self
        )

    @property
    def __m_name__(self) -> str:
        """See :meth:`mockify.abc.IMock.__m_name__`."""
        return self.__name

    @property
    def __m_session__(self) -> ISession:
        """See :meth:`mockify.abc.IMock.__m_session__`."""
        return self.__session

    @property
    def __m_parent__(self) -> typing.Optional[IMock]:
        """See :meth:`mockify.abc.IMock.__m_parent__`."""
        if self.__parent is not None:
            return self.__parent()
        return None
