.. _patching-imported-modules:

Patching imported modules
=========================

.. versionadded:: 0.6

With Mockify you can easily substitute imported module with a mocked version.
Consider following code:

.. testcode::

    import os

    def iter_dirs(path):
        for name in os.listdir(path):
            fullname = os.path.join(path, name)
            if os.path.isdir(fullname):
                yield fullname

That function generates full paths to all direct children directories of
given *path*. And it uses :mod:`os` to make some file system operations. To
test that function without refactoring it you will have to **patch** some
methods of :mod:`os` module. And here's how this can be done in Mockify:

.. testcode::

    from mockify import satisfied, patched
    from mockify.mock import Mock
    from mockify.actions import Return

    def test_iter_dirs():
        os = Mock('os')  # (1)
        os.listdir.expect_call('/tmp').will_once(Return(['foo', 'bar', 'baz.txt']))  # (2)
        os.path.isdir.expect_call('/tmp/foo').will_once(Return(True))  # (3)
        os.path.isdir.expect_call('/tmp/bar').will_once(Return(True))
        os.path.isdir.expect_call('/tmp/baz.txt').will_once(Return(False))

        with patched(os):  # (4)
            with satisfied(os):  # (5)
                assert list(iter_dirs('/tmp')) == ['/tmp/foo', '/tmp/bar']  # (6)

.. testcode::
    :hide:

    test_iter_dirs()

And here's what's going on in presented test:

* We've created *os* mock (1) for mocking **os.listdir()** (2) and
  **os.path.isdir()** (3) methods,
* Then we've used :func:`mockify.patched` context manager (4) that does the
  whole magic of substituting modules matching full names of mocks with
  expectations recorded (which are ``'os.listdir'`` and ``'os.path.isdir'``
  in our case) with corresponding mock objects
* Finally, we've used :func:`mockify.satisfied` context manager (5) to ensure
  that all expectations are satisfied, and ran tested function (6) checking
  it's result.

Note that we did not mock :func:`os.path.join` - that will be used from
:mod:`os` module.
