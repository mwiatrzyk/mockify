.. ----------------------------------------------------------------------------
.. docs/source/tutorial.rst
..
.. Copyright (C) 2018 - 2019 Maciej Wiatrzyk
..
.. This file is part of Mockify library documentation
.. and is released under the terms of the MIT license:
.. http://opensource.org/licenses/mit-license.php.
..
.. See LICENSE for details.
.. ----------------------------------------------------------------------------
Tutorial
========

Mocking functions
-----------------

Using ``Function`` class
^^^^^^^^^^^^^^^^^^^^^^^^

This is the most basic mocking utility. Instances of
:class:`mockify.mock.function.Function` are simply used to mock normal Python
functions. You'll need such mocks for example to test code that uses callbacks.

To create function mock you need to import function mock utility::

    >>> from mockify.mock.function import Function

Now you can create function mock using following boilerplate pattern::

    >>> foo = Function('foo')

In the code above we have created function mock named *foo* and assigned it to
variable of same name. Now object ``foo`` can be used like a normal Python
function.

Most examples in this tutorial use function mocks.

Using ``FunctionFactory`` class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: 0.2

You can also create function mocks in easier way by using
:class:`mockify.mock.function.FunctionFactory` class. Objects of this class
simplify function mock creation by allowing it to be created by just attribute
reading. For example, to create ``foo`` and ``bar`` function mocks you just
need to execute following code::

    >>> from mockify.mock.function import FunctionFactory
    >>> factory = FunctionFactory()
    >>> foo = factory.foo
    >>> bar = factory.bar

Now both ``foo`` and ``bar`` are instances of
:class:`mockify.mock.function.Function` class. Of course you do not have to
assign factory attribute to a variable - you can pass it directly, or even pass
entire factory object to code being under test if needed.

Besides simplified mock creation this class also provides
:meth:`mockify.mock.function.FunctionFactory.assert_satisfied` method that
checks if all mocks created by the factory are satisfied. Of course you can
still do this by checking each individually::

    >>> foo.assert_satisfied()
    >>> bar.assert_satisfied()

But you will also achieve same result with this::

    >>> factory.assert_satisfied()

Mocking objects
---------------

.. versionadded:: 0.3

.. versionchanged:: 0.5
    Now you don't need to subclass, and the API is the same as for other mock
    classes.

To mock Python objects you need :class:`mockify.mock.object.Object` class::

    >>> from mockify.mock.object import Object

Now you can instantiate like any other mocking utility:

    >>> mock = Object('mock')

Once you have a ``mock`` object, you can inject it into some code being under
test. For example, let's have following function that interacts with some
``obj`` object::

    >>> def uut(obj):
    ...     for x in obj.spam:
    ...         obj.foo(x)
    ...     return obj.bar()

To make *uut* function pass, we have to record expectations for:

    * ``spam`` property to be read once
    * ``foo`` to be called zero or more times (depending on what ``spam`` returns)
    * ``bar`` to be called once and to return value that will also be used as
      *uut* function return value

We can of course create several combinations of expectations listed above (due
to use of loop by *uut* function), but for the sake of simplicity let's
configure ``spam`` to return ``[1]`` list, forcing ``foo`` to be called once
with ``1``::

    >>> from mockify.actions import Return
    >>> mock.spam.fget.expect_call().will_once(Return([1]))
    <mockify.Expectation: mock.spam.fget()>
    >>> mock.foo.expect_call(1)
    <mockify.Expectation: mock.foo(1)>
    >>> mock.bar.expect_call().will_once(Return(True))
    <mockify.Expectation: mock.bar()>

Let's now call our ``uut`` function. Since we have covered all methods by our
expectations, the mock call will now pass returning ``True`` (as we've set
``bar`` to return ``True``)::

    >>> uut(mock)
    True

And our mock is of course satisfied::

    >>> mock.assert_satisfied()

Recording and verifying expectations
------------------------------------

Mocks with no expectations
^^^^^^^^^^^^^^^^^^^^^^^^^^

When mock is created, it has no expectations set, so it already is satisfied::

    >>> foo = Function('foo')
    >>> foo.assert_satisfied()

Mockify requires each mock to have all needed expectations recorded. But since
``foo`` has no expectations recorded yet, it cannot be called with any
arguments and doing so will result in :exc:`mockify.exc.UninterestedCall`
exception being raised when call is made. For example::

    >>> foo(1, 2)
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: foo(1, 2)

In order to allow ``foo`` to be called with ``(1, 2)`` as parameters, a
matching expectation have to be recorded.

Mocks with one expectation
^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's go back to our mock ``foo`` defined in previous example and record a
matching expectation::

    >>> foo.expect_call(1, 2)
    <mockify.Expectation: foo(1, 2)>

Now we've recorded that ``foo`` is expected to be called once with ``(1, 2)``
as positional arguments. Since the mock now has expectation, it is not
satisfied now, as the expectation was not yet satisfied (previous failed call
does not count)::

    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[...]>:1
    -----------------------------...
        Pattern: foo(1, 2)
       Expected: to be called once
         Actual: never called

As you can see, Mockify is presenting explanatory assertion message. You will
know that only one expectation has failed and will no exactly which expectation
it is as exact file and line number where the expectation was created are
presented. Besides, you will also know how many times the mock is expected to
be called with params matching *Pattern* and how many times it was actually
called.

Each expectation can be in one of three states:

    * **unsatisfied**,
    * **satisfied**
    * and **oversaturated**.

Currently, expectation from example above is in **unsatisfied** state, as it
can still be satisfied by adequate number of matching mock calls. Let's then
call a mock once to make it satisfied::

    >>> foo(1, 2)
    >>> foo.assert_satisfied()

Calling a mock more times than expected is possible and will not cause
:exc:`mockify.exc.UninterestedCall` exception, as this is only used to point
out that there were no expectations found that match given call parameters. But
if expectation is already satisfied and is called again, it becomes
**oversaturated** and the mock will stay unsatisfied for entire its lifetime::

    >>> foo(1, 2)
    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[...]>:1
    -----------------------------...
        Pattern: foo(1, 2)
       Expected: to be called once
         Actual: called twice
    >>> foo(1, 2)
    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[...]>:1
    -----------------------------...
        Pattern: foo(1, 2)
       Expected: to be called once
         Actual: called 3 times

Mocks with many expectations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Usually each mock will have many expectations recorded, as the code being under
test will usually use its dependencies more than once and with many different
parameters. Let's have a look at following simple function::

    >>> def example(count, callback):
    ...     for i in range(count):
    ...         callback(i)

This function is simply calling ``callback`` given number of times and passes
current loop index as an argument on each iteration. If we want to test such
function we basically need 3 tests:

    1) Check if ``callback`` is not called when ``count`` is 0
    2) Check if ``callback`` is called once with 0 when ``count`` is 1
    3) Check if ``callback`` is triggered with 0, 1, ..., N-1 if ``count`` is N

First test can be written as simple as this one::

    >>> callback = Function('callback')
    >>> example(0, callback)
    >>> callback.assert_satisfied()

If ``callback`` gets called, the test will fail with
:exc:`mockify.exc.UninterestedCall` exception. There is also a nicer way to
expect something to not happen but we'll talk about this a bit later.

Second test will look similar to what we've already used in previous examples::

    >>> callback = Function('callback')
    >>> callback.expect_call(0)
    <mockify.Expectation: callback(0)>
    >>> example(1, callback)
    >>> callback.assert_satisfied()

And third test would look like this. For the sake of simplicity let's test our
``example`` function for N=2::

    >>> callback = Function('callback')
    >>> callback.expect_call(0)
    <mockify.Expectation: callback(0)>
    >>> callback.expect_call(1)
    <mockify.Expectation: callback(1)>
    >>> example(2, callback)
    >>> callback.assert_satisfied()

As you can see, we have recorded two expectations. Mockify by default does not
care about order of expectations, so the same can also be achieved if those
expectations are reversed::

    >>> callback = Function('callback')
    >>> callback.expect_call(1)
    <mockify.Expectation: callback(1)>
    >>> callback.expect_call(0)
    <mockify.Expectation: callback(0)>
    >>> example(2, callback)
    >>> callback.assert_satisfied()

.. note::

    There are plans of implementing ordered expectations in future releases of
    Mockify.

Let's now leave our ``example`` function for a while and have a look at how
unsatisfied assertion is rendered in case of multiple failed expectations.
Let's create another mock with two expectations and call ``assert_satisfied``
on it::

    >>> foo = Function('foo')
    >>> foo.expect_call(1)
    <mockify.Expectation: foo(1)>
    >>> foo.expect_call(2)
    <mockify.Expectation: foo(2)>
    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following 2 expectations are not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[...]>:1
    -----------------------------...
        Pattern: foo(1)
       Expected: to be called once
         Actual: never called
    <BLANKLINE>
    at <doctest tutorial.rst[...]>:1
    -----------------------------...
        Pattern: foo(2)
       Expected: to be called once
         Actual: never called

If you now call a mock for the first time and check if it is satisfied, you'll
see that only one unsatisfied expectation has left::

    >>> foo(1)
    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[...]>:1
    -----------------------------...
        Pattern: foo(2)
       Expected: to be called once
         Actual: never called

And if call one remaining expected call, the mock will become satisfied::

    >>> foo(2)
    >>> foo.assert_satisfied()

Using matchers
^^^^^^^^^^^^^^

Sometimes you will need to write single expectation that is supposed to match
multiple argument values. For this purpose, you will need **matchers**.
Matchers are simple objects with overloaded :meth:`object.__eq__` method.
Thanks to matchers you will be able to write expectations that match entire
classes of values, not exact ones. You will find predefined matchers in
:mod:`mockify.matchers` module.

Let's now use :class:`mockify.matchers.Any` matcher to show how it would look
in practice::

    >>> from mockify.matchers import _
    >>> foo = Function('foo')
    >>> foo.expect_call(_)
    <mockify.Expectation: foo(_)>
    >>> foo.expect_call(_)
    <mockify.Expectation: foo(_)>

We've just recorded that we expect ``foo`` to be called twice with exactly one
argument of any kind. So, for example, we can satisfy our mock with this::

    >>> foo([])
    >>> foo('spam')
    >>> foo.assert_satisfied()

Matchers will also allow us to write complex patterns. For example, if mock is
called with dict as an argument and the dict represents JSONRPC request (see:
https://www.jsonrpc.org/specification), we could write expectation that we want
our mock to be execute with request object, but no matter what is the method,
params and ID::

    >>> foo = Function('foo')
    >>> foo.expect_call({'jsonrpc': '2.0', 'method': _, 'params': _, 'id': _})
    <mockify.Expectation: foo({...})>
    >>> foo({'jsonrpc': '2.0', 'method': 'spam', 'params': 123, 'id': 1})
    >>> foo.assert_satisfied()

But if now the mock is called with different dict structure, the call will
fail::

    >>> foo({'jsonrpc': '2.0'})
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: foo({'jsonrpc': '2.0'})

Dealing with unexpected calls
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: 0.4

Now you can change a default strategy for handling uninterested calls for
your mocks.

To change a strategy you need to create a custom
:class:`mockify.Registry` object and use it as a **registry** for your
mock classes.

For example, you can change the strategy to *ignore*, so all unexpected mock
calls will simply be ignored::

    >>> from mockify import Registry

    >>> registry = Registry(uninterested_call_strategy='ignore')

    >>> mock = Function('mock', registry=registry)
    >>> mock(1, 2)
    >>> mock(1, 2, c=3)
    >>> mock()

    >>> mock.assert_satisfied()

And now your mock will only fail if you have an unsatisfied expectation:

    >>> mock.expect_call('spam')
    <mockify.Expectation: mock('spam')>
    >>> mock.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[74]>:1
    -------------------------------
        Pattern: mock('spam')
       Expected: to be called once
         Actual: never called

Configuring expectation objects
-------------------------------

So far, we've done nothing with :class:`mockify..Expectation` object
``expect_call`` method returns. But it has a lot of very handy features that we
are going to discuss right now.

Expecting a mock to be never called
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is very tricky to expect something to never happen as there are infinite
number of possibilities. Besides, especially if it takes time to execute test,
after how many seconds should we say that somethid *did not happpen*? But
sometimes you may need to expect a mock to be never called.

Let's go back to our ``example`` function defined before. There was a test that
callback is never called. The test looked like this::

    >>> callback = Function('callback')
    >>> example(0, callback)
    >>> callback.assert_satisfied()

Although it works fine, there is not visible what we are expecting. Same test
can be done like this::

    >>> from mockify.matchers import _
    >>> callback = Function('callback')
    >>> callback.expect_call(_).times(0)
    <mockify.Expectation: callback(_)>
    >>> example(0, callback)
    >>> callback.assert_satisfied()

As you can see, we've used :meth:`mockify.Expectation.times` method and
called it with 0, meaning that we expect ``callback`` to be called 0 times. Now
the test looks more expressive, but as stated in the beginning, expecting
something to never happen is tricky. No matter if we call ``example`` function,
other function or even nothing instead, the test will still pass::

    >>> from mockify.matchers import _
    >>> callback = Function('callback')
    >>> callback.expect_call(_).times(0)
    <mockify.Expectation: callback(_)>
    >>> callback.assert_satisfied()

Just like normally expectation has expected call count set to one, modifying it
with ``times(0)`` sets this counter to 0, so mock is already satisfied.
Situtation changes when mock gets called::

    >>> callback(0)
    >>> callback.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[...]>:1
    -----------------------------...
        Pattern: callback(_)
       Expected: to be never called
         Actual: called once

Expecting a mock to be called given number of times
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

So far, if we needed to expect a mock to be called more than once we've
recorded two or more expectations with same parameters. But there is a better
way of doing this.

Let's go back to our ``example`` function and third test. We can rewrite it in
following way::

    >>> callback = Function('callback')
    >>> callback.expect_call(_).times(2)
    <mockify.Expectation: callback(_)>
    >>> example(2, callback)
    >>> callback.assert_satisfied()

But actually we've verified only that mock is called twice each time with any
argument. So in fact, if ``example`` calls a mock with fixed argument, then the
test above will still pass. Therefore, we need another matcher to ensure that
mock is called with valid arguments. For that purpose, we'll use
:class:`mockify.matchers.SaveArg`::

    >>> from mockify.matchers import SaveArg
    >>> count = SaveArg()
    >>> callback = Function('callback')
    >>> callback.expect_call(count).times(2)
    <mockify.Expectation: callback(SaveArg)>
    >>> example(2, callback)
    >>> callback.assert_satisfied()
    >>> count.called_with == [0, 1]
    True

Using :class:`mockify.matchers.SaveArg` you will also have to do some
additional assertions like in example above.

Method :meth:`mockify..Expectation.times` allows to configure more then
just fixed expected number of calls. For more information go to the
:mod:`mockify.times` module documentation.

Single actions
^^^^^^^^^^^^^^

Besides setting how many times each mock is expected to be called and with what
arguments, you can also record actions to be executed on each mock call. For
example, we can tell a mock to return given value when it gets called. To do
this, we need to use :meth:`mockify..Expectation.will_once` method::

    >>> from mockify.actions import Return
    >>> foo = Function('foo')
    >>> foo.expect_call().will_once(Return(1))
    <mockify.Expectation: foo()>

If you now check if mock is satisfied, you'll notice that there is additional
information of what action is going to be executed next::

    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[...]>:1
    -----------------------------...
        Pattern: foo()
         Action: Return(1)
       Expected: to be called once
         Actual: never called

So if you now call a mock, it will return 1 and will be satisfied::

    >>> foo()
    1
    >>> foo.assert_satisfied()

But if you now call a mock again it will end up with an exception::

    >>> foo()
    Traceback (most recent call last):
        ...
    mockify.exc.OversaturatedCall: at <doctest tutorial.rst[...]>:1: foo(): no more actions recorded for call: foo()

This is a very special situation, as when actions are recorded it is assumed
that the mock should always return *something*. Therefore, failing to do that
is treated as exception currently.

.. note::

    There are plans to implement default actions, so there will be no such
    exception in that case, but a default action will be executed instead. But
    mock will not be satisfied anyway.

For more actions please proceed to the :mod:`mockify.actions` documentation.

Action chains
^^^^^^^^^^^^^

You can chain :meth:`mockify..Expectation.will_once` method invocations
to end up with action chains being recorded, so each time when mock is called,
next action in a chain is executed. For example, you can record expectation
that mock is going to be called twice, returning 1 on first call and 2 on
second call::

    >>> foo = Function('foo')
    >>> foo.expect_call().will_once(Return(1)).will_once(Return(2))
    <mockify.Expectation: foo()>

When you now check if mock is satisfied, you will be informed that it is
expected to be called twice and that next action is ``Return(1)``::

    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[...]>:1
    -----------------------------...
        Pattern: foo()
         Action: Return(1)
       Expected: to be called twice
         Actual: never called

If you now call a mock, it will return 1::

    >>> foo()
    1

If you now check if it is satisfied, you will notice that one more call is
needed and that next action will be ``Return(2)``::

    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[...]>:1
    -----------------------------...
        Pattern: foo()
         Action: Return(2)
       Expected: to be called twice
         Actual: called once

Finally, if you call a mock for the second time it will return 2 and mock will
become satisfied::

    >>> foo()
    2
    >>> foo.assert_satisfied()

You can of course record different actions type for each call. For list of
available built-in actions or instructions of how to make custom ones please
refer to the :mod:`mockify.actions` module documentation.

Repeated actions
^^^^^^^^^^^^^^^^

Repeated actions allow to set single action that will keep being executed each
time the mock is called. By default, if mock has repeated action set it can be
called any number of times, so mock with repeated action set is initially
satisfied. Repeated actions are recorded using
:meth:`mockify..Expectation.will_repeatedly` method::

    >>> foo = Function('foo')
    >>> foo.expect_call().will_repeatedly(Return(1))
    <mockify.Expectation: foo()>
    >>> foo.assert_satisfied()

And you can call mock with such defined expectation any times you want. For
example, lets call it 3 times. The mock will return 1 on each call and still
will be satisfied::

    >>> for _ in range(3):
    ...     foo()
    1
    1
    1
    >>> foo.assert_satisfied()

You can also use :meth:`mockify..Expectation.times` method to set
expected call count on a repeated action. For example, if you want to record
repeated action that can be executed at most twice, you would write following::

    >>> from mockify.times import AtMost
    >>> foo = Function('foo')
    >>> foo.expect_call().will_repeatedly(Return(1)).times(AtMost(2))
    <mockify.Expectation: foo()>

Such expectation is already satisfied (as at most twice is 0, 1 or 2 calls)::

    >>> foo.assert_satisfied()

But right now if you call a mock 3 times, the mock will no longer be
satisfied::

    >>> for _ in range(3):
    ...     foo()
    1
    1
    1
    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[...]>:1
    -----------------------------...
        Pattern: foo()
         Action: Return(1)
       Expected: to be called at most twice
         Actual: called 3 times

Recording complex expectations
------------------------------

Currently we've used all of the features independently, but actually it is
possible to record expectations that are combination of those. For example, you
can record few single actions, and one repeated::

    >>> foo = Function('foo')
    >>> foo.expect_call().will_once(Return(1)).will_once(Return(2)).will_repeatedly(Return(3))
    <mockify.Expectation: foo()>

Such mock will be expected to be called at least twice, as there are two single
actions in the chain recorded::

    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[...]>:1
    -----------------------------...
        Pattern: foo()
         Action: Return(1)
       Expected: to be called at least twice
         Actual: never called

If now the mock is called for the fist time it will return 1, for the second
time - 2, and after that it will keep returning 3. And of course it will be
satisfied, as all single actions were consumed::

    >>> foo()
    1
    >>> foo()
    2
    >>> for _ in range(3):
    ...     foo()
    3
    3
    3
    >>> foo.assert_satisfied()

You can also set expected call count for repeated action::

    >>> foo = Function('foo')
    >>> foo.expect_call().will_once(Return(1)).will_repeatedly(Return(2)).times(2)
    <mockify.Expectation: foo()>

Now the mock will have to be called exactly 3 times::

    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[...]>:1
    -----------------------------...
        Pattern: foo()
         Action: Return(1)
       Expected: to be called 3 times
         Actual: never called
    >>> foo()
    1
    >>> foo()
    2
    >>> foo()
    2
    >>> foo.assert_satisfied()

Even such combinations are possible::

    >>> foo = Function('foo')
    >>> foo.expect_call().will_once(Return(1)).will_repeatedly(Return(2)).times(2).will_once(Return(3))
    <mockify.Expectation: foo()>

And this time the mock is expected to be called 4 times::

    >>> foo.assert_satisfied()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: following expectation is not satisfied:
    <BLANKLINE>
    at <doctest tutorial.rst[...]>:1
    -----------------------------...
        Pattern: foo()
         Action: Return(1)
       Expected: to be called 4 times
         Actual: never called
    >>> foo()
    1
    >>> for _ in range(2):
    ...     foo()
    2
    2
    >>> foo()
    3
    >>> foo.assert_satisfied()
