import os

from mockify import satisfied, patched
from mockify.actions import Return, Iterate
from mockify.matchers import RegExp


def list_files(path):
    for name in os.listdir(path):
        fullpath = os.path.join(path, name)
        if os.path.isfile(fullpath):
            yield fullpath


def test_list_files(mock_factory):
    os = mock_factory('os')

    os.listdir.expect_call('/tmp').\
        will_once(Iterate(['spam', 'foo.txt', 'bar.txt']))
    os.path.isfile.expect_call('/tmp/spam').\
        will_once(Return(False))
    os.path.isfile.expect_call(RegExp(r'^/tmp/(.+)\.txt$')).\
        will_repeatedly(Return(True)).times(2)

    with patched(os):
        with satisfied(os):
            assert list(list_files('/tmp')) == ['/tmp/foo.txt', '/tmp/bar.txt']
