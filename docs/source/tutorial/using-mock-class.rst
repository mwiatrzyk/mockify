Using **Mock** class
====================

Introduction
------------

In previous versions of Mockify there were multiple mocking utilities for
various use cases. However, that approach was problematic in most cases due
to lack of flexibility, so starting from version 1.0 all those classes were
merged into single, all-purpose, generic :class:`mockify.mock.Mock` class.

Let's first import that class:

.. testcode::

    from mockify.mock import Mock

Now you can instantiate it giving it a name. That name should be the same as
variable it is assigned to and should clearly say what we are mocking, as
that name will also be used in assertion messages:

.. testcode::

    mock = Mock('mock')

You can only use names that are valid Python identifiers. Nested names (like
``"foo.bar.baz"``) are also allowed. But if you try to instantiate that class
with something not being an identifier, :exc:`TypeError` will be raised:

.. doctest::

    >>> Mock('invalid?')
    Traceback (most recent call last):
        ...
    TypeError: Mock name must be a valid Python identifier, got 'invalid?' instead

Mocking functions
-----------------

Okay, let's go back to our newly created *mock* object. That object is
callable, and you can call it with any number of positional and/or keyword
arguments. By calling it you basically **force** it to act as a function, but
that call will this time fail with :exc:`mockify.exc.UninterestedCall`
assertion, as we did not record any expectations so far:

.. doctest::

    >>> mock(1, 2, c=3)
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: No expectations recorded for mock:
    <BLANKLINE>
    at <doctest default[0]>:1
    -------------------------
    Called:
      mock(1, 2, c=3)

To record one, we have to call **expect_call()** method on *mock* object with
exactly the same set of parameters we expect our mock to be called with:

.. testcode::

    mock.expect_call(1, 2, c=3)

And now no exception will be raised if you call it again:

.. testcode::

    mock(1, 2, c=3)

But if you call *mock* with some parameters that were never expected, then
:exc:`mockify.exc.UnexpectedCall` will be raised:

.. doctest::

    >>> mock(1, 2, 3)
    Traceback (most recent call last):
        ...
    mockify.exc.UnexpectedCall: No matching expectations found for call:
    <BLANKLINE>
    at <doctest default[0]>:1
    -------------------------
    Called:
      mock(1, 2, 3)
    Expected (any of):
      mock(1, 2, c=3)

.. note::
    Even if in production code calling ``mock(1, 2, 3)`` is the same as
    calling ``mock(1, 2, c=3)``, in Mockify those are two distinct things. If
    mocked interface is in production code called positionally, and you later
    switch to keyword args, the mock will fail, as it still expects
    positional args (and vice versa).

The last exception was added in version 1.0 to inform that there are existing
expectations for called mock, but none did match the call. And it is up to
you to decide if that's due to invalid call in tested code, or due to lack of
yet another expectation.

Mocking objects with methods
----------------------------

Let's create another mock object:

.. testcode::

    mock = Mock('mock')

And now, let's try to get some random attributes out of it:

.. doctest::

    >>> mock.foo
    <mockify.mock._ChildMock('mock.foo')>
    >>> mock.bar
    <mockify.mock._ChildMock('mock.bar')>

As you can see, each time you get an attribute, a **child mock** is created.
And for each attribute it will only be created once:

.. doctest::

    >>> mock.foo is mock.foo
    True

So basically mock instances can handle method calls, because before a method
is called, Python first needs to get attribute (a method) from object. If you
pass mock, during that step children mock will be created (if not yet
existing), returned and then called:

    >>> mock.baz(1, 2, 3)
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: No expectations recorded for mock:
    <BLANKLINE>
    at <doctest default[0]>:1
    -------------------------
    Called:
      mock.baz(1, 2, 3)

And of course :exc:`mockify.exc.UninterestedCall` will be raised due to lack
of expectations. So let's record one:

.. testcode::

    mock.baz.expect_call(1, 2, 3)

And now you can call that "method" again:

.. testcode::

    mock.baz(1, 2, 3)

So if you want to record "method" call expectation, you have to **get** that
method first, and call **expect_call()** on it with params you expect your
method to be called with.

Mocking functions behind a module
---------------------------------

It is very common practice in Python to call some functions via
module/submodule chain. For example, usually calls to :mod:`os` module are
made like this::

    import os

    # ...

    if os.path.isfile(path):
        content = open(path).read()

In Mockify, such calls can also be mocked and basically this is extended
version of method call. Here's an example:

.. testcode::

    from mockify.actions import Return

    os = Mock('os')
    os.path.isfile.expect_call('/tmp/foo.txt').will_once(Return(True))

And now if you call **os.path.isfile()** with ``"/tmp/foo.txt"`` as an
argument, the call will return ``True``:

.. doctest::

    >>> os.path.isfile('/tmp/foo.txt')
    True

Mocking setters and getters
---------------------------

You can also mock setters and getters in Mockify. The basic idea is to record
call expectations on **__setattr__()** and **__getattr__()** methods. And
once that expectations are present, all your get/set actions on that
properties will be handled by expectation system.

Here's an example:

.. testcode::

    mock = Mock('mock')
    mock.__setattr__.expect_call('foo', 123)
    mock.__getattr__.expect_call('bar').will_once(Return('spam'))

We've recorded expectation that *mock.foo* will be set once to 123 and that
*mock.bar* will be get once, returning ``'spam'``. Here's how it works:

.. doctest::

    >>> mock.bar
    'spam'
    >>> mock.foo = 123
    >>> mock.foo = 456
    Traceback (most recent call last):
        ...
    mockify.exc.UnexpectedCall: No matching expectations found for call:
    <BLANKLINE>
    at <doctest default[2]>:1
    -------------------------
    Called:
      mock.__setattr__('foo', 456)
    Expected (any of):
      mock.__setattr__('foo', 123)

As you can see, attempt to set attribute to some other value causes
:exc:`mockify.exc.UnexpectedCall` error - like for any other calls with non
matching arguments.

You can also record property set/get expectations for module-level
attributes. Here's an example of setting value for *os.path.sep* attribute:

.. testcode::

    os = Mock('os')
    os.path.__getattr__.expect_call('sep').will_once(Return('/'))

And if you get it now:

.. doctest::

    >>> os.path.sep
    '/'

There is no limit in how deep you can go.

Creating ad-hoc data objects
----------------------------

Besides mocking attribute setting and getting, you can also set a value and
convert mock into data object. That may be useful if you need to return non
scalar return value from some function. For example:

.. testcode::

    response = Mock('response')
    response.data = 'foo bar baz'
    response.headers = {'Content-Length': 11}

    http = Mock('http')
    http.get.expect_call().will_once(Return(response))

And here's what will be returned when you call **http.get()** method:

.. doctest::

    >>> response = http.get()
    >>> response.data
    'foo bar baz'
    >>> response.headers
    {'Content-Length': 11}

And of course - like for methods and properties - you can set values on
nested attributes:

.. doctest::

    >>> mock = Mock('mock')
    >>> mock.foo.bar.baz = 123
    >>> mock.foo.bar.baz
    123

Returning mock from a mock
--------------------------

In previous section we've used **Mock** class to create data object that was
returned by some other mock. In fact, you can also return mocks with
expectations using that approach. This might be usefull to mock call chains,
like this one:

.. testcode::

    foo = Mock('foo')
    foo.to_json.expect_call().will_once(Return('OK'))

    bar = Mock('bar')
    bar.get_response.expect_call().will_once(Return(foo))

    baz = Mock('baz')
    baz.expect_call().will_once(Return(bar))

And now let's call it, starting from *baz*:

.. doctest::

    >>> baz().get_response().to_json()
    'OK'

This is how it works:

* at first, *baz* is called and it returns *bar* mock
* then, **get_response()** is called on *bar*, and as a result *foo* mock is returned,
* finally, **to_json()** is called on a *foo* mock, returning string ``'OK'``.
