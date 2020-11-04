.. ----------------------------------------------------------------------------
.. docs/source/tutorial/setting-expected-call-count.rst
..
.. Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
..
.. This file is part of Mockify library documentation
.. and is released under the terms of the MIT license:
.. http://opensource.org/licenses/mit-license.php.
..
.. See LICENSE for details.
.. ----------------------------------------------------------------------------

.. _setting-expected-call-count:

Setting expected call count
===========================

Expecting mock to be called given number of times
-------------------------------------------------

When you create expectation, you **implicitly** expect your mock to be called
**exactly once** with given given params:

.. testcode::

    from mockify import satisfied
    from mockify.mock import Mock

    foo = Mock('foo')
    foo.expect_call(1, 2)
    with satisfied(foo):
        foo(1, 2)

But what if we need our mock to be called exactly N-times?

First solution is simply to **repeat expectation exactly N-times**. And
here's example test that follows this approach, expecting ``foo`` mock to be
called exactly three times:

.. testcode::

    from mockify import satisfied
    from mockify.mock import Mock

    def func_caller(func, a, b, count):
        for _ in range(count):
            func(a, b)

    def test_func_caller():
        foo = Mock('foo')
        for _ in range(3):
            foo.expect_call(1, 2)
        with satisfied(foo):
            func_caller(foo, 1, 2, 3)

.. testcode::
    :hide:

    test_func_caller()

Although that will certainly work, it is not the best option, as it
unnecessary complicates test code. So here's another example, presenting
recommended solution for setting expected call count to fixed value:

.. testcode::

    def test_func_caller():
        foo = Mock('foo')
        foo.expect_call(1, 2).times(3)  # (1)
        with satisfied(foo):
            func_caller(foo, 1, 2, 3)

.. testcode::
    :hide:

    test_func_caller()

We've removed loop from test function and instead used
:meth:`mockify.Expectation.times` method (1), giving it expected number of
calls to ``foo(1, 2)``. Thanks to this, our expectation is self-explanatory
and in case of unsatisfied assertion you will see that expected call count in
error message:

.. doctest::

    >>> from mockify import assert_satisfied
    >>> from mockify.mock import Mock
    >>> foo = Mock('foo')
    >>> foo.expect_call().times(3)
    <mockify.Expectation: foo()>
    >>> assert_satisfied(foo)
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: Following expectation is not satisfied:
    <BLANKLINE>
    at <doctest default[3]>:1
    -------------------------
    Pattern:
      foo()
    Expected:
      to be called 3 times
    Actual:
      never called

Expecting mock to be never called
---------------------------------

Although expecting something to never happen is a bit tricky, here we can use
it to overcome :exc:`mockify.exc.UninterestedCall` and
:exc:`mockify.exc.UnexpectedCall` assertions. Normally, if mock is called
with parameters for which there are no matching expectations, the call will
fail with one of mentioned exceptions. But you can change that to
:exc:`mockify.exc.Unsatisfied` assertion with following simple trick:

.. testcode::

    from mockify import assert_satisfied
    from mockify.mock import Mock

    foo = Mock('foo')
    foo.expect_call(-1).times(0)  # (1) #

    assert_satisfied(foo)

As you can see, the mock is satisfied despite the fact it **does have**
an expectation recorded at (1). But that expectation has expected call count
set to zero with ``times(0)`` call. And that's the trick - you are explicitly
**expecting** *foo* to be **never** called (or called zero times) with -1 as
an argument.

And now if you make a matching call, the mock will instantly become
unsatisfied:

.. doctest::

    >>> foo(-1)
    >>> assert_satisfied(foo)
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: Following expectation is not satisfied:
    <BLANKLINE>
    at <doctest default[0]>:5
    -------------------------
    Pattern:
      foo(-1)
    Expected:
      to be never called
    Actual:
      called once

And that's the whole trick.

Setting expected call count using **cardinality objects**
---------------------------------------------------------

Previously presented :meth:`mockify.Expectation.times` can also be used in
conjunction with so called **cardinality objects** available via
:mod:`mockify.cardinality` module.

Here's an example of setting **minimal** expected call count:

.. testcode::

    from mockify.mock import Mock
    from mockify.cardinality import AtLeast

    foo = Mock('foo')
    foo.expect_call().times(AtLeast(1))  # (1)

In example above we've recorded expectation that ``foo()`` will be called
**at least once** by passing :class:`mockify.cardinality.AtLeast` instance to
``times()`` method. So currently it will not be satisfied, because it is not
called yet:

.. doctest::

    >>> from mockify import assert_satisfied
    >>> assert_satisfied(foo)
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: Following expectation is not satisfied:
    <BLANKLINE>
    at <doctest default[0]>:5
    -------------------------
    Pattern:
      foo()
    Expected:
      to be called at least once
    Actual:
      never called

But after it is called and made satisfied:

.. doctest::

    >>> foo()
    >>> assert_satisfied(foo)

It will be satisfied forever - no matter how many times ``foo()`` will be
called afterwards:

.. doctest::

    >>> for _ in range(10):
    ...     foo()
    >>> assert_satisfied(foo)

Using the same approach you can also set:

* **maximal** call count (:class:`mockify.cardinality.AtMost`),
* or **ranged** call count (:class:`mockify.cardinality.Between`).
