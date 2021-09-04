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

from pkg_resources import DistributionNotFound, get_distribution

from . import _utils, core

Call = _utils.mark_import_deprecated(
    core.Call, 'mockify.Call', 'mockify.core.Call', '(unreleased)'
)
Expectation = _utils.mark_import_deprecated(
    core.Expectation, 'mockify.Expectation', 'mockify.core.Expectation', '(unreleased)'
)
LocationInfo = _utils.mark_import_deprecated(
    core.LocationInfo, 'mockify.LocationInfo', 'mockify.core.LocationInfo',
    '(unreleased)'
)
Session = _utils.mark_import_deprecated(
    core.Session, 'mockify.Session', 'mockify.core.Session', '(unreleased)'
)
assert_satisfied = _utils.mark_import_deprecated(
    core.assert_satisfied, 'mockify.assert_satisfied',
    'mockify.core.assert_satisfied', '(unreleased)'
)
ordered = _utils.mark_import_deprecated(
    core.ordered, 'mockify.ordered', 'mockify.core.ordered', '(unreleased)'
)
patched = _utils.mark_import_deprecated(
    core.patched, 'mockify.patched', 'mockify.core.patched', '(unreleased)'
)
satisfied = _utils.mark_import_deprecated(
    core.satisfied, 'mockify.satisfied', 'mockify.core.satisfied', '(unreleased)'
)

__author__ = 'Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>'
__released__ = 2019
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = '0.12.0'  # Use 'inv tag' to update this

__all__ = [
    'Call', 'LocationInfo', 'Session', 'Expectation', 'assert_satisfied',
    'ordered', 'satisfied', 'patched'
]
