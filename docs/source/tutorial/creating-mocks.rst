Using mocks in tests
====================

Introduction
------------

To create a mock, you have to first import :class:`mockify.mock.Mock` class:

.. testcode::

    from mockify.mock import Mock

And then instantiate giving it a name. The rule of thumb is to name the mock
using the same name as variable it is assigned to. This is however not
strictly checked, it's just a recommendation. Here's an example:

.. testcode::

    mock = Mock('mock')

Mock names are later used in assertion messages to point you to the mock that
failed. You can only use names that are valid Python identifiers. If you give
an invalid name, mock's constructor will fail:

.. doctest::

    >>> foo = Mock(123)
    Traceback (most recent call last):
        ...
    TypeError: Mock name must be a valid Python identifier, got 123 instead

Instances of **Mock** class can be used to mock:

* functions,
* object methods and properties,
* function calls via module object (f.e. ``os.path.isfile``).

You'll see how in upcoming sections.

Mocking functions
-----------------

Look at following function:

.. testcode::

    def async_sum(a, b, callback):
        callback(a + b)

This is a pseudo-asynchronous function that triggers *callback* with sum of
its two arguments. To test that function using Mockify we need to mock
*callback* and pass it as *async_sum*'s third argument. Here's a complete
test with comments:

.. testcode::

    from mockify import satisfied
    from mockify.mock import Mock

    def test_async_sum():
        # 1) Creating `callback` mock
        callback = Mock('callback')
        # 2) Recording expectation that `callback` will be triggered once with
        #    3 as argument (the sum of 1 and 2). Here we are expecting `callback`
        #    to be a function.
        callback.expect_call(3)
        # 3) Running unit under test under `satisfied()` context manager that
        #    checks if all expectations recorded on `callback` mock are satisfied.
        with satisfied(callback):
            async_sum(1, 2, callback)

.. testcleanup::

    test_async_sum()

Comments:

* We've converted *callback* object into callable by calling **expect_call()**
  method on it.
* We've used :func:`mockify.satisfied` context manager. It checks if all
  expectations have passed once wrapped scope is left. Besides, it clearly
  emphasizes part of the test when setup is done and test execution is
  started.

Mocking methods
---------------

Look at following class:

.. testcode::

    class StreamReader:

        def __init__(self, stream, chunk_size=4096):
            self._stream = stream
            self._chunk_size = chunk_size

        def read(self, count):
            result = b''
            bytes_left = count
            while bytes_left > 0:
                chunk = self._stream.read(min(self._chunk_size, bytes_left))
                bytes_left -= len(chunk)
                result += chunk
            return result

That class implements a decorator pattern on top of some underlying *stream*.
That decorator ensures that **StreamReader.read()** will always read given
amount of bytes - not less, not more. It is assumed that single read from
underlying *stream* can only return up to given maximal amount of bytes, but
never more.

To test that class we need to mock *stream*. And this is no longer a function
- it must provide **read()** method, accepting single integer argument. Look
at following complete test to see how this is done:

.. testcode::

    from mockify import satisfied
    from mockify.mock import Mock
    from mockify.actions import Return

    def test_read_data_chunked_into_three_chunks():
        # 1) Creating `stream` mock and recording call expectation on
        #    `stream.read` property
        stream = Mock('stream')
        stream.read.expect_call(4).will_once(Return(b'foo '))
        stream.read.expect_call(4).will_once(Return(b'bar '))
        stream.read.expect_call(3).will_once(Return(b'baz'))
        # 2) Creating unit under test and injecting `stream` mock
        uut = StreamReader(stream, chunk_size=4)
        # 3) Running the test
        with satisfied(stream):
            assert uut.read(11) == b'foo bar baz'

.. testcleanup::

    test_read_data_chunked_into_three_chunks()

Comments:

* Mock is created exactly the same as in previous example - just a different
  name is picked for it.
* We've recorded call expectation on *stream.read* property, making it
  callable like we did for *callback* object in previous example.
* We've recorded three expectations on that property, because we want to test
  if reading from underlying stream works properly. Since *chunk_size* is 4,
  and we are reading 11 bytes, we will have 3 calls to *stream.read* - that's
  why there are three expectations.
* We've used **will_once()** method to record action to be executed, and used
  :class:`mockify.actions.Return` action to set return value. When
  *stream.read* is called, those values are returned one by one, producing the
  output of **StreamReader.read()** method.
* You can record multiple expectations.

Mocking property getting
------------------------

Look at following function:

.. testcode::

    def unpack(obj, *attrs):
        for name in attrs:
            yield getattr(obj, name)

It iterates over given attribute names, tries to get value for each, and then
yields a value. This can be used to unpack some attributes and convert into
tuple. Here's how we can test such function:

.. testcode::

    from mockify import satisfied, ordered
    from mockify.mock import Mock
    from mockify.actions import Return

    def test_unpack():
        obj = Mock('obj')
        obj.__getattr__.expect_call('foo').will_once(Return(1))
        obj.__getattr__.expect_call('bar').will_once(Return(2))
        with satisfied(obj):
            with ordered(obj):
                assert tuple(unpack(obj, 'foo', 'bar')) == (1, 2)

.. testcleanup::

    test_unpack()

Comments:

* Recording *obj.foo* and *obj.bar* property get expectation is done by
  recording **call** expectation on magic method **__getattr__()**, with
  property names as arguments.
* Additionally, we've used :func:`mockify.ordered` context manager. It ensures,
  that expectations of given object(-s) will be resolved in their **declaration
  order**. Without that context manager, function **unpack()** would return
  same tuple object even if order of attribute names would be different.

Mocking property setting
------------------------

Look at following function:

.. testcode::

    def setattrs(obj, **attrs):
        for name, value in attrs.items():
            setattr(obj, name, value)

It iterates over named arguments and for each sets it in given *obj*. This
can be used to simplify object initialization when you need to assign
multiple attributes. Here's how we can test that function:

.. testcode::

    def test_setattrs():
        obj = Mock('obj')
        obj.__setattr__.expect_call('foo', 1)
        obj.__setattr__.expect_call('bar', 2)
        with satisfied(obj):
            setattrs(obj, foo=1, bar=2)

.. testcleanup::

    test_setattrs()

Comments:

* Like in previous example, to set expectation that *obj.foo* and *obj.bar*
  will be set, we had to record call expectation, but this time on
  **__setattr__()** magic method. And it accepts two arguments: property name
  and value.
* All other magic methods that will come in future releases of Mockify will
  have expectations recorded in that way. Thanks to this approach, no other
  method is needed and everything can be handled with **expect_call()**. That
  makes it easier to remember how to record various expectations.

Mocking modules
---------------

Look at following class:

.. testcode::

    import os

    class File:

        def __init__(self, path):
            self._path = path

        def __eq__(self, other):
            return self.path == other.path

        @property
        def path(self):
            return self._path

    class Directory:

        def __init__(self, path, os=os):
            self._path = path
            self._os = os

        def __eq__(self, other):
            return self.path == other.path

        def __iter__(self):
            for name in self._os.listdir(self._path):
                fullpath = self._os.path.join(self._path, name)
                if self._os.path.isdir(fullpath):
                    yield self.__class__(fullpath, os=self._os)
                elif self._os.path.isfile(fullpath):
                    yield File(fullpath)

        @property
        def path(self):
            return self._path

This class wraps :mod:`os` module behind some high level interface to access
filesystem. You can create *Directory* class giving it a path, and then use
it to iterate over files and directories under given path. And then it yields
*File* object for any file found, and *Directory* (recursively) for
directories. As you can see, *os* parameter is optional and actual :mod:`os`
module was given as a default value. We don't care about that parameter in
production code, however we do care when it comes to test that classes - this
is where our mock will be injected in. And here's example test:

.. testcode::

    from mockify import satisfied
    from mockify.mock import Mock
    from mockify.actions import Return, Invoke
    from mockify.matchers import _

    def is_dir(path):
        return '.' not in path

    def is_file(path):
        return not is_dir(path)

    def join(*paths):
        return '/'.join(paths)

    def test_iterate_over_directory_containing_one_subdir_and_one_file():
        os = Mock('os')
        os.listdir.expect_call('/tmp').will_once(Return(['bar', 'foo.txt']))
        os.path.join.expect_call(_, _).will_repeatedly(Invoke(join))  # (3)
        os.path.isdir.expect_call(_).will_repeatedly(Invoke(is_dir))  # (4)
        os.path.isfile.expect_call('/tmp/foo.txt').will_once(Invoke(is_file))
        with satisfied(os):
            assert [x for x in Directory('/tmp', os=os)] ==\
                [Directory('/tmp/bar'), File('/tmp/foo.txt')]

.. testcleanup::

    test_iterate_over_directory_containing_one_subdir_and_one_file()

Comments:

* This is quite advanced example, as a lot of features were introduced.
* We've created mock named *os* using exactly the same constructor as in all
  other examples
* Call to **expect_call()** method makes first property on the **left** of it
  callable - all other before it form module path or a namespace. Thanks to
  this you can record expectations on module functions (like
  **os.path.isdir()** used here) in very easy and consistent way.
* We've used :class:`mockify.actions.Invoke` action for running custom
  functions when mock is called
* In (3) and (4) We've used :class:`mockify.matchers.Any` **matcher** (imported
  as underscore) and **will_repeatedly()** method. These two functionalities
  combined in this example form a mock that can be called with any argument
  values (although the count must match) and any number of times. Therefore,
  these mocks are actually **stubs** that perform user-defined actions when
  called.
