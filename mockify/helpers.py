# ---------------------------------------------------------------------------
# mockify/helpers.py
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
from ._engine import assert_satisfied

warnings.warn(
    f"Module {__name__!r} was merged to library core and is now available via "
    f"{_new_name!r} - please adjust your imports, as this module will be "
    f"removed in one of upcoming releases.", DeprecationWarning)
