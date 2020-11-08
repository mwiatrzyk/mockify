.. ----------------------------------------------------------------------------
.. docs/source/tutorial/creating-mocks.rst
..
.. Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
..
.. This file is part of Mockify library documentation
.. and is released under the terms of the MIT license:
.. http://opensource.org/licenses/mit-license.php.
..
.. See LICENSE for details.
.. ----------------------------------------------------------------------------
.. _creating-mocks:

Creating mocks and recording expectations
=========================================

Introduction
------------

Since version 0.6 Mockify provides single :class:`mockify.mock.Mock` class
for mocking things. With that class you will be able to mock:

* functions,
* objects with methods,
* modules with functions,
* setters and getters.

That new class can create attributes when you first access them and then you
can record **expectations** on that attributes. Furthermore, that attributes
are **callable**. When you call one, it consumes previously recorded
expectations.

To create a mock, you need to import :class:`mockify.mock.Mock` class and
instantiate it with a name of choice:

.. testcode::

    from mockify.mock import Mock

    foo = Mock('foo')

That name should reflect what is being mocked and this should be function,
object or module name. You can only use names that are valid Python
identifiers or valid Python module names, with submodules separated with a
period sign.

Now let's take a brief introduction to what can be done with just created
*foo* object.

Mocking functions
-----------------

Previously created *foo* mock can be used to mock a function or any other
callable. Consider this example code:

.. testcode::

    def async_sum(a, b, callback):
        result = a + b
        callback(result)

We have "asynchronous" function that calculates sum of *a* and *b* and
triggers given *callback* with a sum of those two. Now, let's call that
function with *foo* mock object as a *callback*. This will happen:

.. doctest::

    >>> async_sum(2, 3, foo)
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: No expectations recorded for mock:
    <BLANKLINE>
    at <doctest default[0]>:3
    -------------------------
    Called:
      foo(5)

Now you should notice two things:

* Mock object *foo* is **callable** and was called with 5 (2 + 3 = 5),
* Exception :exc:`mockify.exc.UninterestedCall` was raised, caused by lack of
  **expectations** on mock *foo*.

Raising that exception is a default behavior of Mockify. You can change this
default behavior (see :attr:`mockify.Session.config` for more details), but
it can be very useful, because it will make your tests fail early and you
will see what expectation needs to be recorded to move forward. In our case
we need to record **foo(5)** call expectation.

To do this you will need to call **expect_call()** method on *foo* object:

.. testcode::

    foo.expect_call(5)

Calling **expect_call()** records call expectation on rightmost mock
attribute, which is *foo* in this case. Given arguments must match the
arguments the mock will later be called with.

And if you call *async_sum* again, it will now pass:

.. testcode::

    from mockify.core import satisfied

    with satisfied(foo):
        async_sum(2, 3, foo)

Note that we've additionally used :func:`mockify.core.satisfied`. It's a context
manager for wrapping portions of test code that **satisfies** one or more
given mocks. And mock is satisfied if all expectations recorded for it are
satisfied, meaning that they were called **exactly** expected number of
times. Alternatively, you could also use :func:`mockify.core.assert_satisfied`
function:

.. testcode::

    from mockify.core import assert_satisfied

    foo.expect_call(3)
    async_sum(1, 2, foo)
    assert_satisfied(foo)

That actually work in the same way as context manager version, but can be
used out of any context, for example in some kind of teardown function.

Mocking objects with methods
----------------------------

Now let's take a look at following code:

.. testcode::

    class APIGateway:

        def __init__(self, connection):
            self._connection = connection

        def list_users(self):
            return self._connection.get('/api/users')

This class implements a facade on some lower level *connection* object. Let's
now create instance of *APIGateway* class. Oh, it cannot be created without a
*connection* argument... That's not a problem - let's use a **mock** for that:

.. testcode::

    connection = Mock('connection')
    gateway = APIGateway(connection)

If you now call *APIGateway.list_users()* method, you will see similar error
to the one we had earlier:

.. doctest::

    >>> gateway.list_users()
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: No expectations recorded for mock:
    <BLANKLINE>
    at <doctest default[0]>:7
    -------------------------
    Called:
      connection.get('/api/users')

And again, we need to record matching expectation to move test forward. To
record method call expectation you basically need to do the same as for
functions, but with additional attribute - a method object:

.. testcode::

    connection.get.expect_call('/api/users')
    with satisfied(connection):
        gateway.list_users()

And now it works fine.

Mocking functions behind a namespace or module
----------------------------------------------

This kind of mocking is extended version of previous one.

Now consider this example:

.. testcode::

    class APIGateway:

        def __init__(self, connection):
            self._connection = connection

        def list_users(self):
            return self._connection.http.get('/api/users')

We have basically the same example, but this time our *connection* interface
was divided between various protocols. You can assume that *connection*
object handles entire communication with external world by providing a facade
to lower level libs. And *http* part is one of them.

To mock that kind of stuff you basically only need to add another attribute
to *connection* mock, and call **expect_call()** on that attribute. Here's a
complete example:

.. testcode::

    connection = Mock('connection')
    gateway = APIGateway(connection)
    connection.http.get.expect_call('/api/users')
    with satisfied(connection):
        gateway.list_users()

Creating ad-hoc data objects
----------------------------

Class :class:`mockify.mock.Mock` can also be used to create ad-hoc data
objects to be used as a response for example. To create one, you just need to
instantiate it, and assign values to automatically created properties. Like
in this example:

.. testcode::

    mock = Mock('mock')
    mock.foo = 1
    mock.bar = 2
    mock.baz.spam.more_spam = 'more spam' # (1)

The most cool feature about data objects created this way is (1) - you can
assign values to any nested attributes. And now let's get those
values:

.. doctest::

    >>> mock.foo
    1
    >>> mock.bar
    2
    >>> mock.baz.spam.more_spam
    'more spam'

Mocking getters
---------------

Let's take a look at following function:

.. testcode::

    def unpack(obj, *names):
        for name in names:
            yield getattr(obj, name)

That function yields attributes extracted from given *obj* in order specified
by *names*. Of course it is a trivial example, but we'll use a mock in place
of *obj* and will record expectations on property getting. And here's the
solution:

.. testcode::

    from mockify.actions import Return

    obj = Mock('obj')
    obj.__getattr__.expect_call('a').will_once(Return(1))  # (1)
    obj.__getattr__.expect_call('b').will_once(Return(2))  # (2)
    with satisfied(obj):
        assert list(unpack(obj, 'a', 'b')) == [1, 2]  # (3)

As you can see, recording expectation of getting property on (1) and (2) is
that you record **call expectation** on a magic method *__getattr__*. And
similar to data objects, you can record getting attribute expectation at any
nesting level - just prefix **expect_call()** with **__getattr__** attribute
and you're done.

Mocking setters
---------------

Just like getters, setters can also be mocked with Mockify. The difference is
that you will have to use **__setattr__.expect_call()** this time and
obligatory give two arguments:

* attribute name,
* and value you expect it to be set with.

Here's a complete solution with a *pack* function - a reverse of the one used
in previous example:

.. testcode::

    def pack(obj, **kwargs):
        for name, value in kwargs.items():
            setattr(obj, name, value)

    obj = Mock('obj')
    obj.__setattr__.expect_call('a', 1)
    obj.__setattr__.expect_call('b', 2)
    with satisfied(obj):
        pack(obj, a=1, b=2)

And that also work on nested attributes.

Correlated setters and getters
------------------------------

Setters and getters mocks are not correlated by default; if you set both
**__setattr__** and **__getattr__** expectations on one property, those
two will be treated as two separate things. Two correlate them, you will have
to do record a bit more complex expectations and use
:class:`mockify.actions.Invoke` to store value in between. Here's an example:

.. testcode::

    from mockify.actions import Invoke
    from mockify.matchers import Type

    store = Mock('store') # (1)

    obj = Mock('obj')
    obj.__setattr__.expect_call('value', Type(int)).will_once(Invoke(setattr, store)) # (2)
    obj.__getattr__.expect_call('value').will_repeatedly(Invoke(getattr, store))  # (3)

In example above we are intercepting property setting and getting with
**setattr()** and **getattr()** built-in functions invoked by
:class:`mockify.actions.Invoke` action. Those functions are bound with mock
(1) acting as a data store and it will be used as first argument. Moreover,
we've recorded setting expectation with a help of
:class:`mockify.matchers.Type` matcher (2), that will only match integer values.
Finally, we've used **will_repeatedly()** at (3), so we are expecting any
number of value reads after it was set. This is how it works in practice:

.. doctest::

    >>> obj.value = 123
    >>> obj.value
    123
    >>> obj.value
    123
