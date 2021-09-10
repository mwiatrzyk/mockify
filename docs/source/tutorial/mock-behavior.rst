.. ----------------------------------------------------------------------------
.. docs/source/tutorial/mock-behavior.rst
..
.. Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
..
.. This file is part of Mockify library documentation
.. and is released under the terms of the MIT license:
.. http://opensource.org/licenses/mit-license.php.
..
.. See LICENSE for details.
.. ----------------------------------------------------------------------------

Most common assertions
======================

Uninterested mock calls
-----------------------

Just after mock object is created, it does not have any expectations
recorded. Calling a mock with no expectations is by default not possible and
results in :exc:`mockify.exc.UninterestedCall` assertion and test
termination:

.. doctest::

    >>> from mockify.mock import Mock
    >>> mock = Mock('mock')
    >>> mock()
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: No expectations recorded for mock:
    <BLANKLINE>
    at <doctest default[2]>:1
    -------------------------
    Called:
      mock()

That error will be raised for any attribute you would call on such mock with
no expectations. That default behavior can be changed (see
:ref:`using-sessions` for more details), but it can get really useful. For
example, if you are writing tests for existing code, you could write tests in
step-by-step mode, recording expectations one-by-one.

Unexpected mock calls
---------------------

This new behavior was introduced in version 0.6.

It is meant to differentiate mocks that has **no** expectations from mocks
that have **at least one**, but not matching **actual** call. This is
illustrated by following example:

.. testcode::

    from mockify.mock import Mock

    mock = Mock('mock')
    mock.expect_call(1, 2)

We have mock *mock* that is expected to be called with 1 and 2 as two
positional arguments. And now, if that mock is called with unexpected
parameters, for instance 1 and **3**, :exc:`mockify.exc.UnexpectedCall`
assertion will be raised:

.. doctest::

    >>> mock(1, 3)
    Traceback (most recent call last):
        ...
    mockify.exc.UnexpectedCall: No matching expectations found for call:
    <BLANKLINE>
    at <doctest default[0]>:1
    -------------------------
    Called:
      mock(1, 3)
    Expected (any of):
      mock(1, 2)

That error is basically extended version of previous **uninterested call**
error, with additional list of existing expectations. That will make it
easier to decide if expectation has a typo, or if there is a bug in tested
code.

Unsatisfied and satisfied mocks
-------------------------------

All previously presented assertion errors can only be raised during mock
call. But even if mock is called with expected parameters and for each call
matching expectation is found, we still need a way to verify if expectations
we've recorded are **satisfied**, which means that all are called expected
number of times.

To check if mock is satisfied you can use :func:`mockify.core.assert_satisfied`
function. This function can be used more than once, but usually the best
place to check if mock is satisfied is at the end of test function.

Each newly created mock is already satisfied:

.. testcode::

    from mockify.core import assert_satisfied
    from mockify.mock import Mock

    foo = Mock('foo')

    assert_satisfied(foo)

Let's now record some expectation:

.. testcode::

    foo.bar.expect_call('spam')

When expectation is recorded, then mock becomes **unsatisfied**, which means
that it is not yet or not fully consumed. That will be reported with
:exc:`mockify.exc.Unsatisfied` assertion:

.. doctest::

    >>> assert_satisfied(foo)
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: Following expectation is not satisfied:
    <BLANKLINE>
    at <doctest default[0]>:1
    -------------------------
    Pattern:
      foo.bar('spam')
    Expected:
      to be called once
    Actual:
      never called

The exception will print out all unsatisfied expectations with their:

* location in test code,
* call pattern that describes function or method with its parameters,
* expected call count of the pattern,
* and actual call count.

By reading exception we see that our method is expected to be called once and
was never called. That's true, because we've only recorded an expectation so
far. To make *foo* satisfied again we need to call the method with params
that will match the expectation:

.. testcode::

    from mockify.core import satisfied

    with satisfied(foo):
        foo.bar('spam')

In example above we've used :func:`mockify.core.satisfied` context manager instead
of :func:`mockify.core.assert_satisfied` presented above. Those two work in
exactly the same way, raising exactly the same exceptions, but context
manager version is better suited for simple tests or when you want to mark
part of test code that satisfies all given mocks.

If you now call our expected method again, the call will not raise any
exceptions:

.. testcode::

    foo.bar('spam')

And even if you run it 5 more times, it will still just work:

.. testcode::

    for _ in range(5):
        foo.bar('spam')

But the mock will no longer be satisfied even after first of that additional
calls:

.. doctest::

    >>> assert_satisfied(foo)
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: Following expectation is not satisfied:
    <BLANKLINE>
    at <doctest default[0]>:1
    -------------------------
    Pattern:
      foo.bar('spam')
    Expected:
      to be called once
    Actual:
      called 7 times

So once again, we have :exc:`mockify.exc.Unsatisfied` raised. But as you can
see, the mock was called 7 times so far, while it still is expected to be
called exactly once.

Why there was no exception raised on second call?

Well, this was made like this actually to make life easier. Mockify allows
you to record very sophisticated expectations, including expected call count
ranges etc. And when mock is called it does not know how many times it will be
called during the test, so we must explicitly tell it that testing is done.
And that's why :func:`mockify.core.assert_satisfied` is needed. Moreover, it is
the only single assertion function you will find in Mockify (not counting its
context manager counterpart).
