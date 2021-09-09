# ---------------------------------------------------------------------------
# mockify/core/_call.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

# pylint: disable=missing-module-docstring

import traceback
import typing

from mockify import _globals, _utils
from mockify.abc import ICall, ICallLocation

__all__ = export = _utils.ExportList()


@export
class Call(ICall):
    """Default implementation of the :class:`mockify.abc.ICall` interface.

    :param __m_fullname__:
        The full name of a mock

    :param `*args`:
        Positional arguments

    :param `**kwargs`:
        Named arguments

    .. versionchanged:: 0.13
        Now this inherits from :class:`mockify.abc.ICall` abstract base class
    """

    def __init__(
        self, __m_fullname__: str, *args: typing.Any, **kwargs: typing.Any
    ):
        _utils.validate_mock_name(__m_fullname__)
        self._name = __m_fullname__
        self._args = args
        self._kwargs = kwargs
        self._location = self._CallLocation.get_external()

    def __str__(self):
        return "{}({})".format(
            self._name, self._format_params(*self._args, **self._kwargs)
        )

    def __repr__(self):
        return "<mockify.core.{}({})>".format(
            self.__class__.__name__,
            self._format_params(self._name, *self._args, **self._kwargs)
        )

    @staticmethod
    def _format_params(*args, **kwargs):
        return _utils.ArgsKwargsFormatter().format(*args, **kwargs)

    @property
    def name(self):
        """See :attr:`mockify.abc.ICall.name`."""
        return self._name

    @property
    def args(self):
        """See :attr:`mockify.abc.ICall.args`."""
        return self._args

    @property
    def kwargs(self):
        """See :attr:`mockify.abc.ICall.kwargs`."""
        return self._kwargs

    @property
    def location(self):
        """See :attr:`mockify.abc.ICall.location`."""
        return self._location

    class _CallLocation(ICallLocation):

        def __init__(self, filename, lineno):
            self._filename = filename
            self._lineno = lineno

        def __str__(self):
            return "{}:{}".format(self._filename, self._lineno)

        @property
        def filename(self):
            """See :attr:`mockify.abc.ICallLocation.filename`."""
            return self._filename

        @property
        def lineno(self):
            """See :attr:`mockify.abc.ICallLocation.lineno`."""
            return self._lineno

        @classmethod
        def get_external(cls):
            stack = traceback.extract_stack()
            for frame in reversed(stack):
                # TODO: make this if statement better
                if not frame.filename.startswith(_globals.ROOT_DIR) and\
                   not frame.filename.startswith('/usr/lib'):
                    return cls(frame.filename, frame.lineno)
            return cls('unknown', -1)


@export
class LocationInfo(Call._CallLocation):
    """A placeholder for file name and line number obtained from the stack.

    Used by :class:`mockify.core.Call` objects to get their location in the
    code. That information is later used in assertion messages.

    .. deprecated:: 0.13
        This is now made private and will be completely removed in next major
        release.

    .. versionadded:: 0.6

    :param filename:
        Name of the file

    :param lineno:
        Line number in given file
    """
    _issue_deprecation_warning = True

    def __init__(self, filename: str, lineno: int):
        if self._issue_deprecation_warning:
            _utils.warn_removed("mockify.core.LocationInfo", '0.13')
        super().__init__(filename, lineno)

    @classmethod
    def get_external(cls):
        _utils.warn_removed("mockify.core.LocationInfo", '0.13')
        cls._issue_deprecation_warning = False
        obj = super().get_external()
        cls._issue_deprecation_warning = True
        return obj
