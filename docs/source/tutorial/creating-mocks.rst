.. ----------------------------------------------------------------------------
.. docs/source/tutorial/creating-mocks.rst
..
.. Copyright (C) 2018 - 2020 Maciej Wiatrzyk
..
.. This file is part of Mockify library documentation
.. and is released under the terms of the MIT license:
.. http://opensource.org/licenses/mit-license.php.
..
.. See LICENSE for details.
.. ----------------------------------------------------------------------------
Creating mocks
==============

Importing **Mock** class
------------------------

Let's start by importing :class:`mockify.mock.Mock` class:

.. testcode::

    from mockify.mock import Mock

This class is an all-in-one mock class that you can use to mock functions,
object methods, modules, properties and more.

Naming mocks
------------

Every mock in Mockify must have a name.

You name your mocks simply during object construction:

.. testcode::

    foo = Mock('foo')

Here we have mock named *foo* created. As you can see the mock has the same
name as variable it was assigned to. Of course you are free to use any other
name, but generally that's the pattern you should follow to avoid confusion -
especially when your tests are starting to fail.

Mocking callable objects
------------------------

Look at following function:

.. testcode::

    def async_add(a, b, callback):
        callback(a + b)

This is a pseudo-asynchronous function that triggers *callback* with a sum of
*a* and *b*.

Now let's create another mock that we'll use as a *callback* argument in that
function. We'll use the pattern introduced earlier:

.. testcode::

    callback = Mock('callback')

If you now call *async_add()* function giving it our mocked callback you'll
notice following exception:

.. doctest::

    >>> async_add(3, 5, callback)
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: callback(8)

It is caused because we did not expect *callback* to be called with 8 as an
argument. Now let's record our first **expectation** to overcome this:

.. doctest::

    callback.expect_call(8)

Above we are implicitly saying that *callback* is expected to be called
exactly once with 8 as a single argument. Try running *async_add()* again to
see that no exception is raised now:

.. testcode::

    async_add(3, 5, callback)

.. note::
    You'll learn how actually expectations work later in this tutorial.

Mocking object methods
----------------------

Look at following class:

.. testcode::

    class EchoProtocol:

        def __init__(self, connection):
            self._connection = connection

        def run(self):
            while True:
                data_received = self._connection.read()
                if not data_received:
                    break
                self._connection.write(data_received)

This is a very primitive echo protocol implementation. That class have a
single dependency to *connection* object that is supposed to have two
methods: *read()* and *write()*.

To mock *connection* object you simply create yet another mock:

.. testcode::

    connection = Mock('connection')

And now let's create *EchoProtocol* class giving it previously created mock
as an argument and call it's *run()* method. This will happen:

.. doctest::

    >>> protocol = EchoProtocol(connection)
    >>> protocol.run()
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: connection.read()
