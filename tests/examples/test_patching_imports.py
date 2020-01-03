# ---------------------------------------------------------------------------
# tests/examples/test_patching_imports.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import os

from mockify import satisfied, patched
from mockify.mock import Mock
from mockify.actions import Return, Iterate
from mockify.matchers import Regex


def list_files(path):
    for name in os.listdir(path):
        fullpath = os.path.join(path, name)
        if os.path.isfile(fullpath):
            yield fullpath


def test_list_files():
    os = Mock('os')

    os.listdir.expect_call('/tmp').\
        will_once(Iterate(['spam', 'foo.txt', 'bar.txt']))
    os.path.isfile.expect_call('/tmp/spam').\
        will_once(Return(False))
    os.path.isfile.expect_call(Regex(r'^/tmp/(.+)\.txt$')).\
        will_repeatedly(Return(True)).times(2)

    with patched(os):
        with satisfied(os):
            assert list(list_files('/tmp')) == ['/tmp/foo.txt', '/tmp/bar.txt']
