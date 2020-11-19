import sys

import asyncio as _asyncio

_py_version = (sys.version_info.major, sys.version_info.minor)


if _py_version >= (3, 7):

    def run(coroutine):
        return _asyncio.run(coroutine)

else:

    def run(coroutine):
        loop = _asyncio.get_event_loop()
        loop.run_until_complete(coroutine)
        loop.close()
