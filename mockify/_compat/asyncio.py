# ---------------------------------------------------------------------------
# mockify/_compat/asyncio.py
#
# Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import asyncio as _asyncio
import sys

_py_version = (sys.version_info.major, sys.version_info.minor)

if _py_version >= (3, 7):

    def run(coroutine):
        return _asyncio.run(coroutine)

else:

    def run(coroutine):
        loop = _asyncio.get_event_loop()
        loop.run_until_complete(coroutine)
