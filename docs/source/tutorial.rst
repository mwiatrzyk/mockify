.. ----------------------------------------------------------------------------
.. docs/source/tutorial.rst
..
.. Copyright (C) 2018 - 2020 Maciej Wiatrzyk
..
.. This file is part of Mockify library documentation
.. and is released under the terms of the MIT license:
.. http://opensource.org/licenses/mit-license.php.
..
.. See LICENSE for details.
.. ----------------------------------------------------------------------------

Tutorial
========

Using **Mock** class
--------------------

Introduction
^^^^^^^^^^^^

Mockify provides a general purpose :class:`mockify.mock.Mock` class for
creating mocks:

.. testcode::

    from mockify.mock import Mock

This class can be used to mock standalone functions, objects with methods and
properties, modules and to create ad-hoc data objects.

To create mock object, you have to name it and, optionally, give it instance of
:class:`mockify.Session` class. Sessions are generally placeholders for
expectation objects. Each mock can create its own session (by default) or use
a shared one. Some features of Mockify work only on shared sessions. You can
read more about sessions in :ref:`Using sessions` section.

To name a mock you must use a name that is a valid Python identifier, or
valid Python module name. It is recommended to use same name as name of
variable the mock is assigned to:

.. testcode::

    foo = Mock('foo')
    foo_bar = Mock('foo.bar')

And if you give invalid name, an exception will be raised:

.. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> Mock('123')
    Traceback (most recent call last):
        ...
    TypeError: Mock name must be a valid Python identifier, got '123' instead

Mock names are important, because they are used in error reports. If you
choose wrong name for your mock, then test failures might potentially be
misleading.

Let's now see how to use mocks in some practical situations.

Mocking functions
^^^^^^^^^^^^^^^^^

We'll start with mocking Python functions.

Look at this function:

.. testcode::

    def find_first(func, iterable):
        for item in iterable:
            if func(item):
                return item

It uses user defined *func* to find first matching element in given
*iterable*. To test that function with Mockify we need to mock *func*, so
let's create a mock *func* first:

.. testcode::

    func = Mock('func')

Mock objects are callable, so basically that is already our function mock.
But if you try to use it before any expectations are recorded, you'll get
:exc:`mockify.exc.UninterestedCall` error:

.. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> find_first(func, [1, 2, 3])
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: No expectations recorded for mock:
    <BLANKLINE>
    at <doctest default[0]>:3
    -------------------------
    Called:
      func(1)
    Expected:
      no expectations recorded

And to record expectations on a function mocks, just use *expect_call* method
like in this example:

.. testcode::

    from mockify.actions import Return

    func.expect_call(1).will_once(Return(True))

We've recorded that *func* will be called with single positional argument of
value ``1`` and, when called, it will return ``True``. Now our example
function will pass and return first item from the sequence:

.. doctest::

    >>> find_first(func, [1, 2, 3])
    1

Mocking methods
^^^^^^^^^^^^^^^
Let's assume we want to test following class:

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

This class is a sort of decorator pattern implementation (in terms of design
patterns) that adds functionality to read exact amount of bytes from
underlying low-level *stream* object which does not guarantee that. To test
*StreamReader* we need to mock *stream* object and its *read()* method.

First of all, we need to create a mock:

.. testcode::

    stream = Mock('stream')

Now let's use the mock and call *StreamReader.read()* method. We'll receive
:exc:`mockify.exc.UninterestedCall` error:

.. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> reader = StreamReader(stream, chunk_size=2)
    >>> reader.read(3)
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: No expectations recorded for mock:
    <BLANKLINE>
    at <doctest default[0]>:11
    --------------------------
    Called:
      stream.read(2)
    Expected:
      no expectations recorded

As you can see, *StreamReader* tried to call
*stream.read()* method but failed due to lack of expectations. To record
expectations on mock's "methods" you have to prefix *expect_call()*
additionally with method's name, like in example below:

.. testcode::

    stream.read.expect_call(2).will_once(Return(b'AB'))
    stream.read.expect_call(1).will_once(Return(b'C'))

We have two expectations, because we expect *StreamReader* to read single
message with two calls to underlying *stream* object. That's because we've
set maximal chunk size to be less than requested byte count.

And let's try to read once again - it will return ``b'ABC'``, the
concatenation of what we've given in expectations:

.. doctest::

    >>> reader.read(3)
    b'ABC'

Mocking property getters and setters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::
    Since version 1.0.0 of Mockify, recording property getting and setting is
    implemented in form of recording call expectation of *__getattr__* and
    *__setattr__* (accordingly) special methods. That makes it clear,
    consistent with the rest of the library and easy to remember and
    understand.

Mocking getters
~~~~~~~~~~~~~~~

For example, let's record that *foo* property will be get once and it will
return ``'foo value'`` when called:

.. testcode::

    mock = Mock('mock')
    mock.__getattr__.expect_call('foo').will_once(Return("foo value"))

Now if you get *foo*, it will return the value:

.. doctest::

    >>> mock.foo
    'foo value'

But since we've recorded single return value, getting it once again will
result in :exc:`mockify.exc.OversaturatedCall` exception:

.. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> mock.foo
    Traceback (most recent call last):
        ...
    mockify.exc.OversaturatedCall: Following expectation was oversaturated:
    <BLANKLINE>
    at <doctest default[0]>:2
    -------------------------
    Pattern:
      mock.__getattr__('foo')
    Expected:
      to be called once
    Actual:
      oversaturated by mock.__getattr__('foo') at <doctest default[0]>:1 (no more actions)

That is not intuitive, why can't we just retrieve the property again? Well,
in fact we are not getting any properties, but calling a mock behind the
scenes and it has only single action recorded. But we can set persistent
values as well using *will_repeatedly()* function (more about that in
:ref:`Recording actions` secion):

.. testcode::

    mock.__getattr__.expect_call('foo').will_repeatedly(Return('spam'))

And now you can call it any times you want, each time returning same value:

.. doctest::

    >>> mock.foo
    'spam'
    >>> mock.foo
    'spam'

Mocking setters
~~~~~~~~~~~~~~~

To mock a setter, you basically need to do the same, but this time with
*__setattr__* special method. For example, to record that *foo* will be once
set to ``123`` we need following expectation:

.. testcode::

    mock = Mock('mock')
    mock.__setattr__.expect_call('foo', 123)

This time the expectation is a bit different, because *__setattr__* accepts
two arguments (name and value), and returns nothing, so we don't need to
record any actions.

Now you can set *foo* to ``123``:

.. testcode::

    mock.foo = 123

But not to any other value, as there is no matching expectation that would
handle that:

.. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> mock.foo = 456
    Traceback (most recent call last):
        ...
    mockify.exc.UnexpectedCall: No matching expectations found for call:
    <BLANKLINE>
    at <doctest default[0]>:1
    -------------------------
    Called:
      mock.__setattr__('foo', 456)
    Expected (any of):
      mock.__setattr__('foo', 123)

And also, since we've recorded that property will be set **once**, attempt to
set it for the second time will make expectation unsatisfied:

.. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> from mockify import satisfied
    >>> with satisfied(mock):
    ...     mock.foo = 123
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: Following expectation is not satisfied:
    <BLANKLINE>
    at <doctest default[0]>:2
    -------------------------
    Pattern:
      mock.__setattr__('foo', 123)
    Expected:
      to be called once
    Actual:
      called twice

Mocking setters and getters simultaneously
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can record both setting and getting expectations for same property. For
example like that:

.. testcode::

    mock = Mock('mock')
    mock.__setattr__.expect_call('foo', 123)
    mock.__getattr__.expect_call('foo').will_repeatedly(Return(123))

We've just recorded that *foo* will once be set to ``123``, and then it will
have that value set forever. Look:

.. doctest::

    >>> mock.foo = 123
    >>> mock.foo
    123
    >>> mock.foo
    123

Basically, we've emulated read/write property. The test would fail if you set
*foo* to some other value or if you set it more times than expected.

Creating ad-hoc data objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes you may need to return some non-scalar value from your mock.
Consider following example:

.. testcode::

    class API:

        def __init__(self, connection):
            self._connection = connection

        def list_users(self):
            response = self._connection.get('/users')
            if response.code != 200:
                raise Exception('failed to list users')
            return response.json['users']

This class is a facade on top of some *connection* class performing HTTP
queries. To test that class, we need to mock *connection.get()* method, but
that method returns a non-scalar result. We can prepare such *response*
object ad-hoc, using :class:`mockify.mock.Mock` class.

Here's an example:

.. testcode::

    response = Mock('response')
    response.code = 200
    response.json = {'users': ['foo', 'bar']}

    connection = Mock('connection')
    connection.get.expect_call('/users').will_once(Return(response))

    api = API(connection)

And now when you call *list_users()*, it will return what we've just told it
to return:

.. doctest::

    >>> api.list_users()
    ['foo', 'bar']

.. tip::
    If you need such data object in more than one test, then you can make
    some factory or fixture function that will save you some work.

Mocking modules (a.k.a. namespaces)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All features of :class:`mockify.mock.Mock` we've discussed so far can also be
used in form of module paths or namespaces.

For example, to expect call of a method of some nested object to be called,
you just record following expectation:

.. testcode::

    mock = Mock('mock')
    mock.foo.bar.expect_call().will_once(Return(123))

We've just recorded that *bar()* method of some nested object *foo* will be
called. Now we can call it:

.. doctest::

    >>> mock.foo.bar()
    123

And we can do the same with setters and getters:

.. testcode::

    mock = Mock('mock')
    mock.foo.__setattr__.expect_call('bar', 123)
    mock.foo.__getattr__.expect_call('bar').will_once(Return(123))

We've just recorded that *bar* property on nested object *foo* will be set
and get once:

.. doctest::

    >>> mock.foo.bar = 123
    >>> mock.foo.bar
    123

And with data objects as well:

.. doctest::

    >>> mock = Mock('mock')
    >>> mock.foo.bar = 123
    >>> mock.foo.bar
    123

And there is no limit of how deep you can go:

.. testcode::

    mock = Mock('mock')
    mock.it.can.be.very.deep.nested.object.path.expect_call().will_once(Return('indeed'))
    assert mock.it.can.be.very.deep.nested.object.path() == 'indeed'

That makes it pretty easy to mock any nested object calls.

Using **MockFactory** class
---------------------------

.. .. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> partial()
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: No expectations recorded for mock:
    <BLANKLINE>
    at <doctest default[0]>:11
    --------------------------
    Called:
      func()
    Expected:
      no expectations recorded

Using sessions
--------------

Recording actions
-----------------
