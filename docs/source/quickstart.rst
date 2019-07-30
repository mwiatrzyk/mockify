Quickstart
==========

Mockify does not try to re-implement :mod:`unittest.mock` from standard
library, but instead it introduces a very different approach of mocking
things.

First thing you need to know is that in Mockify you record **expectations**
on your mocks **before** those are called from the code you are testing.
That's the main difference between Mockify and :mod:`unittest.mock`. If you
are not familiar with that approach it may seem a bit confusing to you, but I
hope you will enjoy it once you see it in action.

Let me now show how this works in practice by writing simple test using
Mockify to mock stuff.

The code to be tested
---------------------

Look at following function:

.. testcode::

    def run_async(task, callback, *args, **kwargs):
        result = task(*args, **kwargs)
        callback(result)

This is a very primitive "asynchronous" task runner. The function, once
called, calls *task* with given arguments and its result is later passed to
the *callback*.

Creating mocks
--------------

To write a test for **run_async** function we need to create mocks first. For
that purpose we'll use :class:`mockify.mock.Function` that is meant to mock
arbitrary functions:

.. testcode::

    from mockify.mock import Function

    task = Function('task')
    callback = Function('callback')

In code above we've created two function mocks - one to mock *task* and one
to mock *callback*. We can now use that mocks like we would use normal
functions. Let's then call **run_async** function and see what happens:

.. doctest::

    >>> run_async(task, callback, 1, 2, c=3)
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: task(1, 2, c=3)

As you've noticed, the code failed with :exc:`mockify.exc.UninterestedCall`
exception, meaning that we have called a mock that does not have matching
expectation set.

Let's now record one.

Recording first expectation
---------------------------

Every mock in Mockify provides **expect_call** method to record call
expectations. This method must be called with exactly the same kind and
number of arguments as the mock is later called with. For example, if mock is
called with 2 positional and 1 named argument we must explicitly set such
expectation. Expecting 3 positional arguments is not the same as expecting 2
positional and 1 named - even if values are the same. Besides, names of
keyword args are also important.

Let's go back to our example and set an expectation on *task* mock (the one
that failed earlier). For function mocks we'll write it like this:

.. doctest::

    >>> task.expect_call(1, 2, c=3)
    <mockify.Expectation: task(1, 2, c=3)>

We've just recorded an expectation that *task* function will be called once
with given arguments. As you've noticed, **expect_call** method have returned
:class:`mockify.Expectation` object that is bound to mock and arguments we've
given in expectation. And since we haven't call a mock yet we can do a lot of
things using that returned expectation object, including side effects chain
recording or maximal call count setting.

We'll go back to this later, but for now let's just call our function again:

.. doctest::

    >>> run_async(task, callback, 1, 2, c=3)
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: callback(None)

As you can see, our function have failed again, but on another call, so we've
moved forward, but another expectation is needed. But why *callback* was
called with ``None``? Well, each mock by default returns ``None`` when
called, and we did not record anything other.

Let's change that.

Recording remaining expectations
--------------------------------

Now we are going to record two expectations, as both functions are called
once **run_async** is called. But now we'll record a different return value
for *task* function, so the *callback* will get something other than
``None``.

Here are our expectations again:

.. testcode::

    from mockify.actions import Return

    task.expect_call(1, 2, c=3).will_once(Return('spam'))
    callback.expect_call('spam')

As you can see, now we are doing something more with our expectation object
recorded on *task* mock. We've called a **will_once** method that is used to
record **next** action to be performed once mock is called (yes, you can
record more and each can be different!). And we've picked a
:class:`mockify.actions.Return` action, that will cause our mock to return
given value once called.

Let's now invoke our code under test.

Invoking code with mocked dependencies
--------------------------------------

As you can see, calling **run_async** will pass now without an error:

.. testcode::

    run_async(task, callback, 1, 2, c=3)

Okay, the code is now running fine, but how do we know if our expectations
were all satisfied? For that purpose we use **assert_satisfied** method or
:func:`mockify.assert_satisfied` context manager, which is highly
recommended.

Since we have two mocks, we need to call **assert_satisfied** on both:

.. testcode::

    task.assert_satisfied()
    callback.assert_satisfied()

And in case of any unsatisfied expectations at least one of that calls will
fail with exception similar to this:

.. testsetup:: grp-1

    from mockify.mock import Function
    callback = Function('callback')
    callback.expect_call(1, 2)

.. doctest:: grp-1

    >>> callback.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest default (setup code)[0]>:3
    --------------------------------------
        Pattern: callback(1, 2)
       Expected: to be called once
         Actual: never called

Putting it all together
-----------------------

Let's sum things up into the final solution:

.. testcode::

    from mockify import assert_satisfied
    from mockify.mock import Function
    from mockify.actions import Return


    def run_async(task, callback, *args, **kwargs):
        """The code to be tested."""
        result = task(*args, **kwargs)
        callback(result)


    def test_run_async():
        """The test."""

        # Step 1: Creating necessary mocks
        task, callback = Function('task'), Function('callback')

        # Step 2: Setting up expectations
        task.expect_call(1, 2, c=3).will_once(Return('spam'))
        callback.expect_call('spam')

        # Step 3: Calling code under test under assert_satisfied() context manager
        with assert_satisfied(task, callback):
            run_async(task, callback, 1, 2, c=3)

.. testcleanup::

    test_run_async()

We've came up with a solution that will most likely become a backbone or a
template for all your tests that will use Mockify to mock things around. Of
course you still can use helper methods or functions, give some extra
assertions etc. - the only important thing here is to always create
expectations **before** mocks are called.
