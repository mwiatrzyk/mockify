# ---------------------------------------------------------------------------
# mockify/mock/object.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import warnings

from . import __name__ as _new_name
from ._object import Object

warnings.warn(
    f"Module {__name__!r} was merged to {_new_name!r} in version 0.5 and "
    f"will be dropped in one of upcoming releases - please update your "
    f"imports.", DeprecationWarning)
