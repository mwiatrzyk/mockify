.. ----------------------------------------------------------------------------
.. docs/source/tutorial/recording-action-chains.rst
..
.. Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
..
.. This file is part of Mockify library documentation
.. and is released under the terms of the MIT license:
.. http://opensource.org/licenses/mit-license.php.
..
.. See LICENSE for details.
.. ----------------------------------------------------------------------------
.. _recording-action-chains:

Recording actions
=================

What are actions used for?
--------------------------

In Mockify, each mocked function by default returns ``None`` when called with
parameters for which expectation was recorded:

.. testcode::

    from mockify.mock import Mock

    foo = Mock('foo')
    foo.expect_call(1)
    foo.expect_call(2)

    assert foo(1) is None
    assert foo(2) is None

That behavior is a normal thing for mocking **command**-like functions, i.e.
functions that **do something** by modifying internal state of an object,
signalling only failures with various exceptions. That functions does not
need or even must not return any values, and in Python function that does not
return anything implicitly returns ``None``.

But there are also **query**-like methods and that kind of methods **must**
return a value of some kind, as we use them to obtain current state of some
object.

So we basically have two problems to solve:

* How to force mocks of command-like functions to raise exceptions?
* How to force mocks of query-like functions to return various values, but
  different than ``None``?

That's where **actions** come in. In Mockify you have various actions
available via :mod:`mockify.actions` module. With actions you can, in
addition to recording expectations, set what the mock will do when called
with matching set of parameters. For example, you can:

* set value to be returned by mock (:class:`mockify.actions.Return`),
* set exception to be raised by mock (:class:`mockify.actions.Raise`),
* set function to be called by mock (:class:`mockify.actions.Invoke`),
* or run your custom action (defined by subclassing
  :class:`mockify.actions.Action` class).

Single actions
--------------

To record single action, you have to use
:meth:`mockify.core.Expectation.will_once` method and give it instance of action
you want your mock to perform. For example:

.. testcode::

    from mockify.mock import Mock
    from mockify.actions import Return

    foo = Mock('foo')
    foo.expect_call(1).will_once(Return('one'))  # (1)
    foo.expect_call(2).will_once(Return('two'))  # (2)

We've recorded two expectations, and set a return value for each. Actions are
tied together with expectations, so in our example we've recorded that
``foo(1)`` will return ``'one'`` (1), and that ``foo(2)`` will return
``'two'``.

Mocks with actions set are not satisfied if there are actions left to be
consumed. If we now check if *foo* is satisfied,
:exc:`mockify.exc.Unsatisfied` will be raised with two unsatisfied
expectations defined in (1) and (2) present:

.. doctest::

    >>> from mockify.core import assert_satisfied
    >>> assert_satisfied(foo)
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: Following 2 expectations are not satisfied:
    <BLANKLINE>
    at <doctest default[0]>:5
    -------------------------
    Pattern:
      foo(1)
    Action:
      Return('one')
    Expected:
      to be called once
    Actual:
      never called
    <BLANKLINE>
    at <doctest default[0]>:6
    -------------------------
    Pattern:
      foo(2)
    Action:
      Return('two')
    Expected:
      to be called once
    Actual:
      never called

Notice that the exception also shows an action to be performed next. That
information is not present if you have no custom actions recorded. Let's now
call *foo* with params matching previously recorded expectations:

.. doctest::

    >>> foo(1)
    'one'
    >>> foo(2)
    'two'
    >>> assert_satisfied(foo)

As you can see, the mock returned values we've recorded. And it is also
satisfied now.

Action chains
-------------

It is also possible to record **multiple** actions on single expectation,
simply by adding more :meth:`mockify.core.Expectation.will_once` method calls:

.. testcode::

    from mockify.mock import Mock
    from mockify.actions import Return

    count = Mock('count')
    count.expect_call().\
        will_once(Return(1)).\
        will_once(Return(2)).\
        will_once(Return(3))

In example above we've created a mock named *count*, and it will consume and
invoke subsequent action on each call:

.. doctest::

    >>> count()
    1
    >>> count()
    2
    >>> count()
    3

That's how action chains work. Of course each chain is tied to a particular
expectation, so you are able to create different chains for different
expectations. And you can have different actions in your chains, and even mix
them.

When multiple single actions are recorded, then mock is implicitly expected
to be called N-times, where N is a number of actions in a chain. But if you
have actions recorded and mock gets called more times than expected, it will
fail on mock call with :exc:`mockify.exc.OversaturatedCall`:

.. doctest::

    >>> count()
    Traceback (most recent call last):
        ...
    mockify.exc.OversaturatedCall: Following expectation was oversaturated:
    <BLANKLINE>
    at <doctest default[0]>:5
    -------------------------
    Pattern:
      count()
    Expected:
      to be called 3 times
    Actual:
      oversaturated by count() at <doctest default[0]>:1 (no more actions)

That error will only be raised if you are using actions. Normally, the mock
would simply be unsatisfied. But it was added for a reason; if there are no
more custom actions recorded and mock is called again, then it would most
likely fail few lines later (f.e. due to invalid value type), but with
stacktrace pointing to tested code, not to call of mocked function. And that
would potentially be harder to debug.

.. _recording-repeated-actions:

Repeated actions
----------------

You also can record so called **repeated** actions with
:meth:`mockify.core.Expectation.will_repeatedly` method instead of previously used
``will_once()``:

.. testcode::

    from mockify.mock import Mock
    from mockify.actions import Return

    foo = Mock('foo')
    foo.expect_call().will_repeatedly(Return(123))  # (1)

Repeated actions defined like in (1) can be executed any number of times,
including zero, so currently mock *foo* is already satisfied:

.. doctest::

    >>> assert_satisfied(foo)

Repeated actions are useful when you need same thing to be done every single
time the mock is called. So if ``foo()`` is now called, it will always return
``123``, as we've declared in (1):

.. doctest::

    >>> [foo() for _ in range(4)]
    [123, 123, 123, 123]

And *foo* will always be satisfied:

.. doctest::

    >>> assert_satisfied(foo)

Repeated actions with cardinality
---------------------------------

You can also declare repeated actions that can only be executed given number
of times by simply adding call to :meth:`mockify.core.Expectation.times` method
just after ``will_repeatedly()``:

.. testcode::

    from mockify.mock import Mock
    from mockify.actions import Return

    foo = Mock('foo')
    foo.expect_call().will_repeatedly(Return(123)).times(1)  # (1)

Such declared expectation will have to be executed exactly once. But of
course you can use any cardinality object from :mod:`mockify.cardinality` to
record even more complex behaviors. The difference between such constrained
repeated actions and actions recorded using ``will_once()`` is that repeated
actions cannot be oversaturated - the mock will simply keep returning value
we've set, but of course will no longer be satisfied:

.. doctest::

    >>> foo()
    123
    >>> assert_satisfied(foo)
    >>> foo()
    123
    >>> assert_satisfied(foo)
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: Following expectation is not satisfied:
    <BLANKLINE>
    at <doctest default[0]>:5
    -------------------------
    Pattern:
      foo()
    Action:
      Return(123)
    Expected:
      to be called once
    Actual:
      called twice

Using chained and repeated actions together
-------------------------------------------

It is also possible to use both single and repeated actions together, like in
this example:

.. testcode::

    from mockify.mock import Mock
    from mockify.actions import Return

    foo = Mock('foo')
    foo.expect_call().\
        will_once(Return(1)).\
        will_once(Return(2)).\
        will_repeatedly(Return(3))

Such declared expectations have implicitly set **minimal** expected call
count that is equal to number of actions recorded using ``will_once()``. So
currently the mock is not satisfied:

.. doctest::

    >>> assert_satisfied(foo)
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: Following expectation is not satisfied:
    <BLANKLINE>
    at <doctest default[0]>:5
    -------------------------
    Pattern:
      foo()
    Action:
      Return(1)
    Expected:
      to be called at least twice
    Actual:
      never called

But the mock becomes satisfied after it is called twice:

.. doctest::

    >>> foo()
    1
    >>> foo()
    2
    >>> assert_satisfied(foo)

And at this point it will continue to be satisfied - no matter how many times
it is called after. And for every call it will execute previously set
repeated action:

.. doctest::

    >>> foo()
    3
    >>> foo()
    3
    >>> assert_satisfied(foo)

Using chained and repeated actions with cardinality
---------------------------------------------------

You can also record expectations like this one:

.. testcode::

    from mockify.mock import Mock
    from mockify.actions import Return

    foo = Mock('foo')
    foo.expect_call().\
        will_once(Return(1)).\
        will_once(Return(2)).\
        will_repeatedly(Return(3)).\
        times(2)  # (1)

Basically, this is a constrained version of previous example in which
repeated action is expected to be called only twice. But total expected call
count is 4, as we have two single actions recorded:

.. doctest::

    >>> assert_satisfied(foo)
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: Following expectation is not satisfied:
    <BLANKLINE>
    at <doctest default[0]>:5
    -------------------------
    Pattern:
      foo()
    Action:
      Return(1)
    Expected:
      to be called 4 times
    Actual:
      never called

Now let's satisfy the expectation by calling a mock:

.. doctest::

    >>> [foo() for _ in range(4)]
    [1, 2, 3, 3]
    >>> assert_satisfied(foo)

Since last of your actions is a repeated action, you can keep calling the
mock more times:

.. doctest::

    >>> foo()
    3

But the mock will no longer be satisfied, as we've recorded at (1) that
repeated action will be called exactly twice:

.. doctest::

    >>> assert_satisfied(foo)
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: Following expectation is not satisfied:
    <BLANKLINE>
    at <doctest default[0]>:5
    -------------------------
    Pattern:
      foo()
    Action:
      Return(3)
    Expected:
      to be called 4 times
    Actual:
      called 5 times
