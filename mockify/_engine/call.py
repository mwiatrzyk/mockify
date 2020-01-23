# ---------------------------------------------------------------------------
# mockify/_engine/call.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import os
import keyword
import traceback

from .. import exc, _utils, _globals


class LocationInfo:
    """Used to extract information about file location.

    .. versionadded:: 1.0
    """

    def __init__(self, filename, lineno):
        self._filename = filename
        self._lineno = lineno

    def __eq__(self, other):
        return type(self) is type(other) and\
            self._filename == other._filename and\
            self._lineno == other._lineno

    def __str__(self):
        return f"{self._filename}:{self._lineno}"

    @property
    def filename(self):
        return self._filename

    @property
    def lineno(self):
        return self._lineno

    @classmethod
    def get_external(cls):
        stack = traceback.extract_stack()
        for frame in reversed(stack):
            if not frame.filename.startswith(_globals.ROOT_DIR) and\
               not frame.filename.startswith('/usr/lib'):  # TODO: make this better
                return cls(frame.filename, frame.lineno)


class Call:
    """An object representing mock call.

    Instances of this class are created when expectations are recorded or
    when mock is called. The role of this class is to keep mock name and its
    call params as a single object for easier comparison between expected and
    actual mock calls.

    This class also provides some basic stack info to be used for error
    reporting (f.e. to display where failed expectation was defined).
    """

    def __init__(self, *args, **kwargs):
        if not args:
            raise TypeError("__init__() missing 1 required positional argument: 'name'")
        self._name = args[0]
        self._args = args[1:]
        self._kwargs = kwargs
        self._location = LocationInfo.get_external()
        _utils.validate_mock_name(self._name)

    def __str__(self):
        return f"{self._name}({self._format_params(*self._args, **self._kwargs)})"

    def __repr__(self):
        return f"<mockify.{self.__class__.__name__}({self._format_params(self._name, *self._args, **self._kwargs)})>"

    def __eq__(self, other):
        return self._name == other._name and\
            self._args == other._args and\
            self._kwargs == other._kwargs

    def __ne__(self, other):
        return not self.__eq__(other)

    def _format_params(self, *args, **kwargs):
        return _utils.format_args_kwargs(*args, **kwargs)

    @property
    def name(self):
        """Mock name."""
        return self._name

    @property
    def args(self):
        """Mock positional args."""
        return self._args

    @property
    def kwargs(self):
        """Mock named args."""
        return self._kwargs

    @property
    def location(self):
        """Location (a tuple containing file name and line number) where this
        call object was created.

        .. versionadded:: 1.0

        This is used to display where failed expectation was declared or
        where failed call was orinally made.
        """
        return self._location
