Mock types
==========

Function mocks
--------------

Functions can be mocked using :class:`mockify.mock.Function` class.

You will need function mocks if code you are testing depends on some
callbacks, key functions, comparators etc. Creating function mocks is easy -
you just need to call constructor giving it a name you want to assign to your
mock:

.. testsetup::

    from mockify.mock import Function
    from mockify.actions import Return

.. testcode::

    foo = Function('foo')

At this point you have your first function mock created, but it does not have
any expectations yet. To record one you simply use **expect_call** method:

.. testcode::

    foo.expect_call(1, 2, c=3).will_once(Return('spam'))

Here we have recorded expectation that *foo* will be called once with exactly
that configuration of arguments and when called it will return *spam*. Let's
call it now to check that:

.. doctest::

    >>> foo(1, 2, c=3)
    'spam'

Finally, you can check if all expectations you've recroded are satisfied
using this assertion call:

.. testcode::

    foo.assert_satisfied()

Function mock factory
---------------------

.. versionadded:: 0.2

You can also create function mocks without boilerplate introduced in previous
example using :class:`mockify.mock.FunctionFactory` class.

Objects of this class simplify function mock creation by allowing it to be
created by just attribute reading. For example, to create function mock named
*foo* you just need to read attribute *foo* of function factory object:

.. testsetup::

    from mockify import assert_satisfied
    from mockify.mock import FunctionFactory
    from mockify.actions import Return

.. doctest::

    >>> factory = FunctionFactory()
    >>> foo = factory.foo
    >>> isinstance(foo, Function)
    True
    >>> foo.name
    'foo'

And any time you access *foo* on same factory object you'll get the same
function mock object. That makes it easy to record expectations directly:

.. testcode::

    factory = FunctionFactory()
    factory.bar.expect_call(1, 2).will_once(Return(3))

And then use factory as object with methods:

.. doctest::

    >>> factory.bar(1, 2)
    3

You can also check if mocks created by factory are all satisfied using one
call:

.. testcode::

    factory.assert_satisfied()

Or same, with context manager:

.. testcode::

    with assert_satisfied(factory):
        pass

So you can also use mock factory for grouping function mocks.

Namespace mocks
---------------

.. versionadded:: 0.5

I don't know how to name it, so let's name it **namespace** :-)

This kind of mock, provided by :class:`mockify.mock.Namespace`, is meant to
be used to mock functions or objects that are behind some kind of a namespace
or module.

For example, it is quite common that in Python we import :mod:`os` directly
and use it like this::

    if os.path.isfile(path):
        with open(path) as fd:
            content = fd.read()

To mock such call with namespace mocks, you simply need to do following:

.. testsetup::

    from mockify.mock import Namespace
    from mockify.actions import Return

.. testcode::

    os = Namespace('os')
    os.path.isfile.expect_call('/tmp/foo.txt').will_once(Return(True))

Now, you can call that mock just like you would use :mod:`os` directly:

.. testcode::

    if os.path.isfile('/tmp/foo.txt'):
        print('It is a file!')

And the output will be following:

.. testoutput::

    It is a file!

Generally speaking, namespace mock is a generalized version of
:class:`mockify.mock.FunctionFactory`, so you can use it instead.

Object mocks
------------

.. versionchanged:: 0.5
    Now you don't need to subclass, and the API is the same as for other mock
    classes.

.. versionadded:: 0.3

Creating object mocks
^^^^^^^^^^^^^^^^^^^^^

Python objects can be mocked using :class:`mockify.mock.Object` class.

You can create object mocks in three ways:

1) By just giving object's name:

    .. testsetup::

        from mockify.mock import Object

    .. testcode::

        first = Object('first')

2) By giving name **and** list of allowed method and/or property names:

    .. testcode::

        second = Object('second', methods=['foo'], properties=['spam'])

3) Or the same as 2), but using inheritance:

    .. testcode::

        class Custom(Object):
            __methods__ = ['foo']
            __properties__ = ['spam']

If object mock is created using 1), then it's actual number of methods and
properties depends on expectations being recorded. In this mode, you can get
any attribute, and it will be returned as a property mock:

.. doctest::

    >>> foo = first.foo
    >>> isinstance(foo, Object.Property)
    True

Such properties are not evaluated instantly, but only when you try to access
data for the first time (f.e. during comparison; that is due to the fact that
getter mock is behind a proxy). And since you did not record *spam* get
expectation, such evaluation will fail with
:exc:`mockify.exc.UninterestedCall` exception:

.. doctest::

    >>> first.foo == 123
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: obj.foo.fget()

If you instead create mocks using 2) or 3), then methods and properties are
all initialized during object's construction and any other will simply cause
:exc:`AttributeError`:

.. doctest::

    >>> isinstance(second.foo, Object.Method)
    True
    >>> isinstance(second.spam, Object.Property)
    True
    >>> bar = second.bar
    Traceback (most recent call last):
        ...
    AttributeError: Mock object 'second' has no attribute 'bar'

Recording method call expectations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Let's now go back to our *first* object and record some method call
expectation. Here's how you can do that:

.. testcode::

    first.foo.expect_call().will_once(Return('spam'))

In example above we are getting *foo* once again (which is a property), and
call **expect_call** on it. This forces *foo* to switch into a method:

.. doctest::

    >>> isinstance(first.foo, Object.Method)
    True

If you now call that method without params, it will return string **spam** as
we've told it to do so once called without params:

.. doctest::

    >>> first.foo()
    'spam'

You can record more method call expectations, or even more expectations to
this particular *foo* mocked method in the very same way.

Recording property get and set expectations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Recording property expectations is very similar to recording method call
expectations. The only difference is that you have to additionally pass one
more extra attribute which is **fget** for getters and **fset** for setters.
Here's an example:

.. testcode::

    first.spam.fset.expect_call(123)
    first.spam.fget.expect_call().will_repeatedly(Return(123))

Thanks to these extra attributes we will not convert property into a method
like in example earlier:

.. doctest::

    >>> isinstance(first.spam, Object.Property)
    True

And now mocked properties in action:

.. doctest::

    >>> first.spam = 123
    >>> first.spam
    123
    >>> first.spam = 'spam'
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: first.spam.fset('spam')

Notice that setting *spam* to "spam" fails - that is due to the fact, that we
did not expect it to be called with "spam", but with 123.

The other thing is that we've recorded both setter and getter to be called
for property *spam*, which is not mandatory - you can record either setter or
getter if needed.

And the last thing is that *spam* is not a normal property, so it does not
keep any values - it simply is a proxy that follows requests to either getter
or setter mock that does the rest.

Verifying expectations
^^^^^^^^^^^^^^^^^^^^^^

Like for :class:`mockify.mock.FunctionFactory` and other similar grouping
mock types, :class:`mockify.mock.Object` provides a single
**assert_satisfied** method that once called checks if all method and
property expectations are satisfied for a particular mocked object:

.. testcode::

    first.assert_satisfied()
