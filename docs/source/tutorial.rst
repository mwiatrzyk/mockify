Tutorial
========

Introduction
------------

Mockify library provides several mocking utilities that all follow these common
principles:

* It is not possible to call a mock without matching expectation recorded;
  doing so will result in :exc:`mockify.exc.UninterestedCall` exception being
  raised::

    >>> from mockify.mock import FunctionMock
    >>> foo = FunctionMock('foo')
    >>> foo(1, 2)
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: at <doctest tutorial.rst[...]>:1: foo(1, 2)


Mocking functions
-----------------

Creating function mocks
^^^^^^^^^^^^^^^^^^^^^^^

Function mocks are used to mock normal Python functions.

Such functions are often used as callbacks and this would be probably the main
use case for function mocking.

Function mocks are provided by ``FunctionMock`` class that can be imported like
this:

.. doctest::

    >>> from mockify.mock import FunctionMock

After class is imported, it can be instantiated into function mock:

.. doctest::

    >>> foo = FunctionMock('foo')

This is a boilerplate pattern for making mock of function named ``foo``.

Calling function mocks
^^^^^^^^^^^^^^^^^^^^^^

Function mocks can be called without arguments or with any combination of
positional and keyword arguments.

The only important thing is that it is necessary to first record expectation
with arguments matching precisely arguments of a call that is expected to be
made. Otherwise the call will fail as in this example:

.. doctest::

    >>> foo(1, 2, c=3)
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: at <doctest tutorial.rst[2]>:1: foo(1, 2, c=3)

Mockify follows strict approach when it comes to registering expectations and
will always fail if there is no matching expectation registered. This will make
it easier to find function invocations that are not meant to be made or to find
missing expectations.

Registering expectations
^^^^^^^^^^^^^^^^^^^^^^^^

To make call from previous example execute successfuly, it is needed to
register expectation using exactly the same arguments as for call. And function
mocks have special ``expect_call`` method for doing this:

.. doctest::

    >>> foo.expect_call(1, 2, c=3)
    <Expectation: call=foo(1, 2, c=3), expected='to be called once', actual='never called'>

This method returns ``Expectation`` object that will allow recording more
sophisticated behaviors like setting expected call count or registering side
effects. But this will be presented in :ref:`Working with expectation objects` part of
this tutorial.

Let's go back to our ``foo`` function mock.

If the mock is now called, it will be executed successfuly, without any
exception:

.. doctest::

    >>> foo(1, 2, c=3)

But if tried to call the same mock with some other arguments, or with lack of
any arguments, the call will fail again:

.. doctest::

    >>> foo()
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: at <doctest tutorial.rst[5]>:1: foo()

And again, if expectation is registered that ``foo`` will be called without
args, then the call ``foo()`` will succeed as well:

.. doctest::

    >>> foo.expect_call()
    <Expectation: call=foo(), expected='to be called once', actual='never called'>
    >>> foo()

And if more expectations are registered, more possible ways of calling ``foo``
will become available to be made without failing.

Verifying registered expectations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Mock function objects have ``assert_satisfied`` method for checking if all
registered expectations are satisfied.

This method can be called several times and in any place in the test code, but
it will most likely be called only once at the end of test function. So the
most typical usage would be following:

.. doctest::

    def test_something():
        foo = FunctionMock('foo')

        foo.expect_call(...)

        uut = SomeUnitUnderTest(foo)
        uut.run()  # foo gets called somewhere here

        foo.assert_satisfied()

Let's now go back to previously created ``foo`` mock function and check if it
is satisfied:

.. doctest::

    >>> foo.assert_satisfied()

You'll see, that it is; we were expecting ``foo`` to be once called without
args, and once with ``(1, 2, c=3)`` and both expectations are already
satisfied.

Let's now call ``foo`` with both expected args one more time:

.. doctest::

    >>> foo()
    >>> foo(1, 2, c=3)

As you can see, the call will not fail - despite the fact, that now the mock is
no longer satisfied:

.. doctest::

    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.UnsatisfiedAssertion: Following expectations have failed:
    <BLANKLINE>
    #1 at <doctest tutorial.rst[3]>:1
    ---------------------------------
          Mock: foo(1, 2, c=3)
      Expected: to be called once
        Actual: called twice
    <BLANKLINE>
    #2 at <doctest tutorial.rst[6]>:1
    ---------------------------------
          Mock: foo()
      Expected: to be called once
        Actual: called twice

Calling a mock will only fail if no matching expectation is found. The only way
to check if expectations are satisfied is to call ``assert_satisfied`` method,
which shows very deep information about which expectations have failed and why.
This is also the only method that needs to be executed; unlike
:mod:`unittest.mock`, Mockify has one single assertion for checking if
expectations are satisfied.

Method ``assert_satisfied`` will also fail if we have expectations registered,
but no calls made yet:

.. doctest::

    >>> bar = FunctionMock('bar')
    >>> bar.expect_call(1, 2, 3)
    <Expectation: call=bar(1, 2, 3), expected='to be called once', actual='never called'>
    >>> bar.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.UnsatisfiedAssertion: Following expectations have failed:
    <BLANKLINE>
    #1 at <doctest tutorial.rst[13]>:1
    ----------------------------------
          Mock: bar(1, 2, 3)
      Expected: to be called once
        Actual: never called

And if we now call ``bar`` according to expectation, ``assert_satisfied`` will
pass:

.. doctest::

    >>> bar(1, 2, 3)
    >>> bar.assert_satisfied()


Working with expectation objects
--------------------------------

Setting expected call count
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The most basic way of setting how many times mock is expected to be called is
to set multiple expectations with same arguments. For example, if it is needed
to record that a mock must be called twice, following expectation can be
recorded:

.. doctest::

    >>> foo = FunctionMock('foo')

    >>> foo.expect_call(1, 2) # doctest: +ELLIPSIS
    ...
    >>> foo.expect_call(1, 2) # doctest: +ELLIPSIS
    ...

And now mock ``foo`` must be called twice to satisfy expectation:

.. doctest::

    >>> for _ in range(2):
    ...     foo(1, 2)
    >>> foo.assert_satisfied()

But actually you have two distinct expectations set in this case and if mock is
called less times than expected (f.e. once), you would have an assertion error
pointing to expectations that were never called instead of telling that mock
was called once and not twice.

The better way is to use ``times`` method and only one expectation. For
example, the same expectation as above can be recorded like this:

.. doctest::

    >>> foo = FunctionMock('foo')
    >>> foo.expect_call(1, 2).times(2)

This time, you have single expectation declared, and assertion error will show
that mock is expected to be called twice:

.. doctest::

    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.UnsatisfiedAssertion: Following expectations have failed:
    <BLANKLINE>
    #1 at <doctest tutorial.rst[23]>:1
    ----------------------------------
          Mock: foo(1, 2)
      Expected: to be called twice
        Actual: never called

And once again, after calling a mock twice, expectation becomes satisfied:

.. doctest::

    >>> for _ in range(2):
    ...     foo(1, 2)
    >>> foo.assert_satisfied()

And if mock is called for the third time, assertion will fail again:

.. doctest::

    >>> foo(1, 2)
    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.UnsatisfiedAssertion: Following expectations have failed:
    <BLANKLINE>
    #1 at <doctest tutorial.rst[23]>:1
    ----------------------------------
          Mock: foo(1, 2)
      Expected: to be called twice
        Actual: called 3 times

It is also possible to expect a mock to be never called. This is achieved by
setting expected call count to zero:

.. doctest::

    >>> foo = FunctionMock('foo')

    >>> foo.expect_call(1, 2).times(0)
    <Times: expected='to be never called', actual='never called'>

Now the mock is satisfied already, because it was not yet called:

.. doctest::

    >>> foo.assert_satisfied()

But if it is called at some point, assertion error would be raised:

.. doctest::

    >>> foo(1, 2)
    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.UnsatisfiedAssertion: Following expectations have failed:
    <BLANKLINE>
    #1 at <doctest tutorial.rst[28]>:1
    ----------------------------------
          Mock: foo(1, 2)
      Expected: to be never called
        Actual: called once

Method ``times`` is not meant to be used only to set exact number of expected
call count. See :mod:`mockify.carinality` module documentation for more
information about setting mock call count.

Recording action chains
^^^^^^^^^^^^^^^^^^^^^^^

Beside setting expected call count, each expectation can have one or more
actions recorded. These actions make *action chain* and are executed in same
order as were declared. Actions are used to tell the mock what it should do on
next call and how many times it is expected to be called.

Please take a look at following example:

.. doctest::

    >>> from mockify.mock import FunctionMock
    >>> from mockify.actions import Return

    >>> foo = FunctionMock('foo')
    >>> foo.expect_call().\
    ...     will_once(Return(1)).\
    ...     will_once(Return(2))

We are expecting mock ``foo`` to be called twice returning ``1`` on first call
and ``2`` on second call. Please notice that ``times`` method was not used at
all. Let's now check if mock is satisfied:

.. doctest::

    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.UnsatisfiedAssertion: Following expectations have failed:

    #1 at <doctest tutorial.rst[0]>:4
    ---------------------------------
          Mock: foo()
        Action: Return(1)
      Expected: to be called once
        Actual: never called

When expectation has actions recorded, assertion error will tell what the mock
is expected to do next. So we now call that mock and print its result:

.. doctest::

    >>> foo()
    1

And if now once again the mock is checked if it is satisfied:

.. doctest::

    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.UnsatisfiedAssertion: Following expectations have failed:

    #1 at <doctest tutorial.rst[0]>:4
    ---------------------------------
          Mock: foo()
        Action: Return(2)
      Expected: to be called once
        Actual: never called
