.. ----------------------------------------------------------------------------
.. docs/source/tutorial/setting-expected-call-count.rst
..
.. Copyright (C) 2018 - 2020 Maciej Wiatrzyk
..
.. This file is part of Mockify library documentation
.. and is released under the terms of the MIT license:
.. http://opensource.org/licenses/mit-license.php.
..
.. See LICENSE for details.
.. ----------------------------------------------------------------------------
Setting expected call count
---------------------------

.. testsetup::

    from mockify.mock import Function

When you record expectation in Mockify, it is by default expected to be
called exactly once. But sometimes such simple expectation is not enough and
you would need to set number of mock calls that makes expectation valid.

For that purpose you can use **times()** method on returned expectation
object. When you use that method, you need to give either exact call count,
or range object available in :mod:`mockify.cardinality` module.

For all examples here we'll use following function mock:

.. testcode::

    foo = Function('foo')

.. note::
    We could use any other mock type here, as recording expectation is
    basically same for every kind of mock. We'll use mostly function mocks in
    this tutorial as those are most trivial.

And set an expectation that the mock will be called exactly 3 times:

.. testcode::

    foo.expect_call().times(3)

And now, if you call a mock only once and check if it is satisfied, you'll
get following error:

.. doctest::

    >>> foo()
    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:

    at <doctest default (setup code)[1]>:2
    --------------------------------------
        Pattern: foo()
       Expected: to be called 3 times
         Actual: called once

To get rid of that, the mock will have to be called two more times:

.. doctest::

    >>> for _ in range(2):
    ...     foo()
    >>> foo.assert_satisfied()

And now, since the mock is satisfied, no exception is raised again.

But what if the mock is called again?

Well, the exception will be there, again:

.. doctest::

    >>> foo()
    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:

    at <doctest default (setup code)[1]>:2
    --------------------------------------
        Pattern: foo()
       Expected: to be called 3 times
         Actual: called 4 times
