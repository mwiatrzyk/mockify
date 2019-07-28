Creating mocks
==============

Mocking functions
-----------------

Functions can be mocked using :class:`mockify.mock.Function` class.

You will need function mocks if code you are testing depends on some
callbacks, key functions, comparators etc. To start mocking function you need
to first import function mock class:

.. testcode::

    from mockify.mock import Function

And now you can create function mock instances by giving a name that is
usually the same as variable we assign to:

.. testcode::

    foo = Function('foo')

At this point you have first function mock created.

Using ``FunctionFactory`` class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: 0.2

You can also create function mocks in easier way by using
:class:`mockify.mock.FunctionFactory` class. Objects of this class
simplify function mock creation by allowing it to be created by just attribute
reading. For example, to create ``foo`` and ``bar`` function mocks you just
need to execute following code::

    >>> from mockify.mock import FunctionFactory
    >>> factory = FunctionFactory()
    >>> foo = factory.foo
    >>> bar = factory.bar

Now both ``foo`` and ``bar`` are instances of
:class:`mockify.mock.Function` class. Of course you do not have to
assign factory attribute to a variable - you can pass it directly, or even pass
entire factory object to code being under test if needed.

Besides simplified mock creation this class also provides
:meth:`mockify.mock.FunctionFactory.assert_satisfied` method that
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

To mock Python objects you need :class:`mockify.mock.Object` class::

    >>> from mockify.mock import Object

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

Creating mocks
--------------

Using ``Function`` class
^^^^^^^^^^^^^^^^^^^^^^^^

This is the most basic mocking utility. Instances of
:class:`mockify.mock.Function` are simply used to mock normal Python
functions. You'll need such mocks for example to test code that uses callbacks.

To create function mock you need to import function mock utility::

    >>> from mockify.mock import Function

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
:class:`mockify.mock.FunctionFactory` class. Objects of this class
simplify function mock creation by allowing it to be created by just attribute
reading. For example, to create ``foo`` and ``bar`` function mocks you just
need to execute following code::

    >>> from mockify.mock import FunctionFactory
    >>> factory = FunctionFactory()
    >>> foo = factory.foo
    >>> bar = factory.bar

Now both ``foo`` and ``bar`` are instances of
:class:`mockify.mock.Function` class. Of course you do not have to
assign factory attribute to a variable - you can pass it directly, or even pass
entire factory object to code being under test if needed.

Besides simplified mock creation this class also provides
:meth:`mockify.mock.FunctionFactory.assert_satisfied` method that
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

To mock Python objects you need :class:`mockify.mock.Object` class::

    >>> from mockify.mock import Object

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

