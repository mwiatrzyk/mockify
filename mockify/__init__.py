# ---------------------------------------------------------------------------
# mockify/__init__.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
"""Library core module.

.. deprecated:: 0.9.0
    Please import from :mod:`mockify.core` module instead. Importing via
    Mockify's root module will stop working since next major release.
"""

from . import _utils, core

Call = _utils.mark_import_deprecated(
    core.Call, 'mockify.Call', 'mockify.core.Call', '0.13'
)
Expectation = _utils.mark_import_deprecated(
    core.Expectation, 'mockify.Expectation', 'mockify.core.Expectation', '0.13'
)
LocationInfo = _utils.mark_import_deprecated(
    core.LocationInfo, 'mockify.LocationInfo', 'mockify.core.LocationInfo',
    '0.13'
)
Session = _utils.mark_import_deprecated(
    core.Session, 'mockify.Session', 'mockify.core.Session', '0.13'
)
assert_satisfied = _utils.mark_import_deprecated(
    core.assert_satisfied, 'mockify.assert_satisfied',
    'mockify.core.assert_satisfied', '0.13'
)
ordered = _utils.mark_import_deprecated(
    core.ordered, 'mockify.ordered', 'mockify.core.ordered', '0.13'
)
patched = _utils.mark_import_deprecated(
    core.patched, 'mockify.patched', 'mockify.core.patched', '0.13'
)
satisfied = _utils.mark_import_deprecated(
    core.satisfied, 'mockify.satisfied', 'mockify.core.satisfied', '0.13'
)

__author__ = 'Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>'
__released__ = 2019
__version__ = '0.13.1'

__all__ = [
    'Call', 'LocationInfo', 'Session', 'Expectation', 'assert_satisfied',
    'ordered', 'satisfied', 'patched'
]
