Tutorial
========

Mocking functions
-----------------

Creating function mocks
^^^^^^^^^^^^^^^^^^^^^^^

Function mocks are used to mock normal Python functions.

Such functions are often used as callbacks and this would be probably the main
use case for function mocking.

Function mocks are provided by ``FunctionMock`` class that can be imported like
this::

    >>> from mockify.mock import FunctionMock

After class is imported, it can be instantiated into function mock::

    >>> foo = FunctionMock('foo')

This is a boilerplate pattern for making mock of function named ``foo``.

Calling function mocks
^^^^^^^^^^^^^^^^^^^^^^

Function mocks can be called without arguments or with any combination of
positional and keyword arguments.

The only important thing is that it is necessary to first record expectation
with arguments matching precisely arguments of a call that is expected to be
made. Otherwise the call will fail as in this example::

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
mocks have special ``expect_call`` method for doing this::

    >>> foo.expect_call(1, 2, c=3)
    <Expectation: call=foo(1, 2, c=3), expected='to be called once', actual='never called'>

This method returns ``Expectation`` object that will allow recording more
sophisticated behaviors like setting expected call count or registering side
effects. But this will be presented in :ref:`Working with expectations` part of
this tutorial.

Let's go back to our ``foo`` function mock.

If the mock is now called, it will be executed successfuly, without any
exception::

    >>> foo(1, 2, c=3)

But if tried to call the same mock with some other arguments, or with lack of
any arguments, the call will fail again::

    >>> foo()
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: at <doctest tutorial.rst[5]>:1: foo()

And again, if expectation is registered that ``foo`` will be called without
args, then the call ``foo()`` will succeed as well::

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
most typical usage would be following::

    def test_something():
        foo = FunctionMock('foo')

        foo.expect_call(...)

        uut = SomeUnitUnderTest(foo)
        uut.run()  # foo gets called somewhere here

        foo.assert_satisfied()

Let's now go back to previously created ``foo`` mock function and check if it
is satisfied::

    >>> foo.assert_satisfied()

You'll see, that it is; we were expecting ``foo`` to be once called without
args, and once with ``(1, 2, c=3)`` and both expectations are already
satisfied.

Let's now call ``foo`` with both expected args one more time::

    >>> foo()
    >>> foo(1, 2, c=3)

As you can see, the call will not fail - despite the fact, that now the mock is
no longer satisfied::

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
but no calls made yet::

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
pass::

    >>> bar(1, 2, 3)
    >>> bar.assert_satisfied()


Working with expectations
-------------------------

Setting how many times the mock can be called
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO
