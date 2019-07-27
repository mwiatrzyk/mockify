# ---------------------------------------------------------------------------
# mockify/engine.py
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
from ._engine import Registry, Call, Expectation

warnings.warn(
    f"Module {__name__!r} is deprecated since 0.5 and will be dropped in one "
    f"of upcoming releases - please import directly from {_new_name!r}.",
    DeprecationWarning)
