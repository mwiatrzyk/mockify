# ---------------------------------------------------------------------------
# mockify/api.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import itertools

from mockify import _utils
from mockify import abc as _abc
from mockify import actions as _actions
from mockify import cardinality as _cardinality
from mockify import core as _core
from mockify import exc as _exc
from mockify import matchers as _matchers
from mockify import mock as _mock
from mockify.abc import *
from mockify.actions import *
from mockify.cardinality import *
from mockify.core import *
from mockify.exc import *
from mockify.matchers import *
from mockify.mock import *

_submodules = [_core, _mock, _abc, _actions, _cardinality, _exc, _matchers]

__all__ = _utils.ExportList.merge_unique(*(x.__all__ for x in _submodules))

__doc__ =\
"""A proxy module providing access to all publicly available classes and
functions.

This module automatically imports public names from all other Mockify's
modules, so any needed class or function can be imported like this:

.. testcode::

    from mockify.api import satisfied, Mock, Return

See the list of available names below.

Rationale behind this module is that testing frameworks like PyTest provide
access to all public names basically via single import, so test helper like
Mockify should also provide similar behaviour. On the other hand, using a root
module to do such imports is discouraged, as it would always import everything
- even if the user does not want to.

.. note::
    Since this is a proxy module, any change to other public modules will
    affect this one, so f.e. removing a class from ``mockify.mock`` module will
    also remove it from ``mockify.api`` module.

Currently available classes and functions are:

{}

.. versionadded:: (unreleased)
""".format('\n'.join(itertools.chain(*(_utils.render_public_members_docstring(x) for x in _submodules))))
