# ---------------------------------------------------------------------------
# tests/examples/test_patching_imports.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import os

from mockify.actions import Iterate, Return
from mockify.core import patched, satisfied
from mockify.matchers import Regex
from mockify.mock import Mock


def list_files(path):
    for name in os.listdir(path):
        fullpath = os.path.join(path, name)
        if os.path.isfile(fullpath):
            yield fullpath


def test_list_files():
    os_mock = Mock('os')

    os_mock.listdir.expect_call('/tmp').\
        will_once(Iterate(['spam', 'foo.txt', 'bar.txt']))
    os_mock.path.isfile.expect_call('/tmp/spam').\
        will_once(Return(False))
    os_mock.path.isfile.expect_call(Regex(r'^/tmp/(.+)\.txt$')).\
        will_repeatedly(Return(True)).times(2)

    with patched(os_mock):
        with satisfied(os_mock):
            assert list(list_files('/tmp')) == ['/tmp/foo.txt', '/tmp/bar.txt']
