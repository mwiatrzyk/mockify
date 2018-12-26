Tutorial
========

Creating mocks
--------------

Function mocks
^^^^^^^^^^^^^^

To create function mock you need to import function mock utility::

    >>> from mockify.mock.function import Function

Now you can create function mock using following boilerplate pattern::

    >>> foo = Function('foo')

Most examples in this tutorial will use function mocks.

Recording expectations
----------------------

Let's create function mock again::

    >>> foo = Function('foo')

This mock does not have any expectations yet, so it is already satisfied. You
can use ``assert_satisfied`` method to verify that statement::

    >>> foo.assert_satisfied()

If there are no expectations, then it will not be possible to call a mock in
any way. Such attempt will raise :exc:`mockify.exc.UninterestedCall` exception
causing test to end with an error. For example::

    >>> foo(1, 2)
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: foo(1, 2)

To avoid exceptions, you must first record expectations representing any call
that is expected to be made. This can be done by ``expect_call`` method::

    >>> foo.expect_call(1, 2)
    <mockify.Expectation: foo(1, 2)>

Now we've created expectation, but mock is currently not satisfied::

    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[5]>:1
    ------------------------------
        Pattern: foo(1, 2)
       Expected: to be called once
         Actual: never called

Now if we call a mock again the call will pass and mock will become satisfied::

    >>> foo(1, 2)
    >>> foo.assert_satisfied()

But what will happen if mock is called again? Well, there will be no exception,
but mock will be no longer satisfied as it was called more times than
expected::

    >>> foo(1, 2)
    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[5]>:1
    ------------------------------
        Pattern: foo(1, 2)
       Expected: to be called once
         Actual: called twice

To allow mock to be called twice you can for example record two expectations
with same parameters::

    >>> foo = Function('foo')
    >>> foo.expect_call(1, 2)
    <mockify.Expectation: foo(1, 2)>
    >>> foo.expect_call(1, 2)
    <mockify.Expectation: foo(1, 2)>

If you now check if mock is satisfied before calling it you'll notice that two
expectations are not satisfied::

    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following 2 expectations are not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[12]>:1
    -------------------------------
        Pattern: foo(1, 2)
       Expected: to be called once
         Actual: never called
    <BLANKLINE>
    at <doctest tutorial.rst[13]>:1
    -------------------------------
        Pattern: foo(1, 2)
       Expected: to be called once
         Actual: never called

And now if you call a mock twice, it will become satisfied, as first call will
satisfy first expectation, and second call - second expectation::

    >>> for _ in range(2):
    ...     foo(1, 2)
    >>> foo.assert_satisfied()

But if in this case mock is called again, only second expectation will
oversaturate::

    >>> foo(1, 2)
    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[13]>:1
    -------------------------------
        Pattern: foo(1, 2)
       Expected: to be called once
         Actual: called twice

There are, however, better ways to record expectations with given expected call
count.

Configuring expectations
------------------------

Setting expected call count to fixed value
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's go back to previous example and create function mock that is expected to
be called twice. But this time we'll use ``times`` method::

    >>> foo = Function('foo')
    >>> foo.expect_call(1, 2).times(2)
    <mockify.Expectation: foo(1, 2)>

Now you can check if ``foo`` is satisfied. You'll see a slightly different
exception, as there is only one expectation now::

    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[20]>:1
    -------------------------------
        Pattern: foo(1, 2)
       Expected: to be called twice
         Actual: never called

If you now call a mock twice, the mock will become satisfied::

    >>> for _ in range(2):
    ...     foo(1, 2)
    >>> foo.assert_satisfied()

And if you call it again, it will oversaturate::

    >>> foo(1, 2)
    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[20]>:1
    -------------------------------
        Pattern: foo(1, 2)
       Expected: to be called twice
         Actual: called 3 times

Expecting mock to be never called
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can also use ``times`` method to create expectation that is expected to be
never called::

    >>> foo = Function('foo')
    >>> foo.expect_call(1, 2).times(0)
    <mockify.Expectation: foo(1, 2)>

Mock with such expectations is already satisfied::

    >>> foo.assert_satisfied()

And oversaturates when called once or more::

    >>> foo(1, 2)
    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[27]>:1
    -------------------------------
        Pattern: foo(1, 2)
       Expected: to be never called
         Actual: called once

Using generalized way of setting expected call count
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There is a special :mod:`mockify.times` module containing set of classes for
generalized call count limiting. For example, let's create a mock that we
expect to be called at most twice::

    >>> from mockify.times import AtMost
    >>> foo = Function('foo')
    >>> foo.expect_call(1, 2).times(AtMost(2))
    <mockify.Expectation: foo(1, 2)>

Since we expected a mock to be called at most twice, then the mock is already
satisfied::

    >>> foo.assert_satisfied()

And it will be still if called once or twice::

    >>> for _ in range(2):
    ...     foo(1, 2)
    ...     foo.assert_satisfied()

But if called for the third time, the mock will no longer be satisfied as we
expected it to be called at most twice::

    >>> foo(1, 2)
    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[33]>:1
    -------------------------------
        Pattern: foo(1, 2)
       Expected: to be called at most twice
         Actual: called 3 times

For more options see :mod:`mockify.times` documentation.
