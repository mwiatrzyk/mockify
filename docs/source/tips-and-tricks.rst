.. ----------------------------------------------------------------------------
.. docs/source/tips-and-tricks.rst
..
.. Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
..
.. This file is part of Mockify library documentation
.. and is released under the terms of the MIT license:
.. http://opensource.org/licenses/mit-license.php.
..
.. See LICENSE for details.
.. ----------------------------------------------------------------------------

Tips & tricks
=============

.. _func-with-out-params:

Mocking functions with output parameters
----------------------------------------

Sometimes you will need to mock calls to interfaces that will force you to
create some kind of object which later is used as an argument to that call.
Value of that object is not constant, it is different on every run, so you
will not be able to record adequate expectation using fixed value. Moreover,
that object is changed by call to mocked interface method. How to mock that
out?

This kind of problem exists in following simple class:

.. testcode::

    import io


    class RemoteFileStorage:

        def __init__(self, bucket):
            self._bucket = bucket

        def read(self, name):
            buffer = io.BytesIO()  # (1)
            self._bucket.download('bucket-name', "uploads/{}".format(name), buffer)  # (2)
            return buffer.getvalue()

That class is kind of a facade on top of some cloud service for accessing
files that were previously uploaded by another part of the application. To
download the file we need to create a buffer (1) which is later passed to
``bucket.download()`` method (2). In production, that method downloads a file
into a buffer, but how to actually mock that in test?

Here's a solution:

.. testcode::

    from mockify import satisfied
    from mockify.mock import Mock
    from mockify.actions import Invoke
    from mockify.matchers import _


    def download(payload, bucket, key, fd):  # (1)
        fd.write(payload)


    def test_reading_file_using_remote_storage():
        bucket = Mock('bucket')

        bucket.download.\
            expect_call('bucket-name', 'uploads/foo.txt', _).\
            will_once(Invoke(download, b'spam'))  # (2)

        storage = RemoteFileStorage(bucket)

        with satisfied(bucket):
            assert storage.read('foo.txt') == b'spam'  # (3)

.. testcode::
    :hide:

    test_reading_file_using_remote_storage()

And here's an explanation:

* We've implemented ``download()`` function - a minimal and dummy
  implementation of ``bucket.download()`` method. Our function simply writes
  given payload to file descriptor created in tested class and passed as a
  last argument.
* We've recorded an expectation that ``bucket.download()`` will be called once
  with three args, having last argument wildcarded using
  :class:`mockify.matchers.Any` matcher. Therefore, buffer object passed to a
  mock will match that expectation.
* We've recorded single :class:`mockify.actions.Invoke` action to execute
  function created in (1), with ``b'spam'`` bytes object bound as first
  argument (that's why ``download()`` function accepts one more argument).
  With this approach we can force ``download()`` to write different bytes -
  depending on out test.
* Finally, we've used assertion at (3) to check if tested method returns
  "downloaded" bytes.
