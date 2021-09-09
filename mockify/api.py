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
import types

from mockify import actions, cardinality, core, exc, matchers, mock

_submodules = (core, mock, actions, cardinality, exc, matchers)

__all__ = []


def _gen_name_list():
    memo = set()
    for module in _submodules:
        yield "* From :mod:`{module.__name__}` module:".format(module=module)
        for name in module.__all__:
            if name not in memo:
                memo.add(name)
                obj = getattr(module, name)
                if isinstance(obj, type):
                    yield "    * :class:`{module.__name__}.{name}`".format(
                        module=module, name=name
                    )
                elif isinstance(obj, types.FunctionType):
                    yield "    * :func:`{module.__name__}.{name}`".format(
                        module=module, name=name
                    )
                else:
                    yield "    * :obj:`{module.__name__}.{name}`".format(
                        module=module, name=name
                    )

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
Mockify should also provide similar behaviour.

.. note::
    Since this is a proxy module, any change to other public modules will
    affect this one, so f.e. removing a class from ``mockify.mock`` module will
    also remove it from ``mockify.api`` module.

Currently available classes and functions are:

{}

.. versionadded:: (unreleased)
""".format('\n'.join(_gen_name_list()))
