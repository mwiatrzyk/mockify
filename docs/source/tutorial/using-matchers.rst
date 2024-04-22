.. ----------------------------------------------------------------------------
.. docs/source/tutorial/using-matchers.rst
..
.. Copyright (C) 2019 - 2024 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
..
.. This file is part of Mockify library documentation
.. and is released under the terms of the MIT license:
.. http://opensource.org/licenses/mit-license.php.
..
.. See LICENSE for details.
.. ----------------------------------------------------------------------------

Using matchers
==============

Introduction
------------

So far we've been recording expectations with fixed argument values. But
Mockify provides to you a very powerful mechanism of **matchers**, available
via :mod:`mockify.matchers` module. Thanks to the matchers you can record
expectations that will match more than just a single value. Let's take a
brief tour of what you can do with matchers!

Recording expectations with matchers
------------------------------------

Let's take a look at following code that we want to test:

.. testcode::

    import uuid


    class ProductAlreadyExists(Exception):
        pass


    class AddProductAction:

        def __init__(self, database):
            self._database = database

        def invoke(self, category_id, name, data):
            if self._database.products.exists(category_id, name):
                raise ProductAlreadyExists()
            product_id = str(uuid.uuid4())  # (1)
            self._database.products.add(product_id, category_id, name, data)  # (2)

That code represents a business logic of adding some kind of product into
database. The product is identified by a **name** and **category**, and there
cannot be more than one product of given name inside given category. But
tricky part is at (1), where we calculate UUID for our new product. That
value is random, and we are passing it into ``products.add()`` method, which
will be mocked. How to mock that, when we don't know what will the value be?
And here comes **the matchers**:

.. testcode::

    from mockify.core import satisfied
    from mockify.mock import Mock
    from mockify.actions import Return
    from mockify.matchers import _  # (1)


    def test_add_product_action():
        database = Mock('database')

        database.products.exists.\
            expect_call('dummy-category', 'dummy-name').\
            will_once(Return(False))
        database.products.add.\
            expect_call(_, 'dummy-category', 'dummy-name', {'description': 'A dummy product'})  # (2)

        action = AddProductAction(database)
        with satisfied(database):
            action.invoke('dummy-category', 'dummy-name', {'description': 'A dummy product'})

.. testcode::
    :hide:

    test_add_product_action()

We've used a **wildcard** matcher imported in (1), and placed it as first
argument of our expectation (2). That underscore object is in fact instance
of :class:`mockify.matchers.Any` and is basically **equal** to every possible
Python object, therefore it will match any possible UUID value, so our test
will pass.

Of course you can also use another matcher if you need a more strict check.
For example, we can use :class:`mockify.matchers.Regex` to check if this
**is** a real UUID value:

.. testcode::

    from mockify.core import satisfied
    from mockify.mock import Mock
    from mockify.actions import Return
    from mockify.matchers import Regex

    any_uuid = Regex(r'^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}$')


    def test_add_product_action():
        database = Mock('database')

        database.products.exists.\
            expect_call('dummy-category', 'dummy-name').\
            will_once(Return(False))
        database.products.add.\
            expect_call(any_uuid, 'dummy-category', 'dummy-name', {'description': 'A dummy product'})

        action = AddProductAction(database)
        with satisfied(database):
            action.invoke('dummy-category', 'dummy-name', {'description': 'A dummy product'})

.. testcode::
    :hide:

    test_add_product_action()

Combining matchers
------------------

You can also combine matchers using ``|`` and ``&`` binary operators.

For example, if you want to expect values that can only be integer numbers or
lower case ASCII strings, you can combine :class:`mockify.matchers.Type` and
:class:`mockify.matchers.Regex` matchers like in this example:

.. testcode::

    from mockify.mock import Mock
    from mockify.actions import Return
    from mockify.matchers import Type, Regex

    mock = Mock('mock')
    mock.\
        expect_call(Type(int) | Regex(r'^[a-z]+$', 'LOWER_ASCII')).\
        will_repeatedly(Return(True))

And now let's try it:

.. doctest::

    >>> mock(1)
    True
    >>> mock('abc')
    True
    >>> mock(3.14)
    Traceback (most recent call last):
        ...
    mockify.exc.UnexpectedCall: No matching expectations found for call:
    <BLANKLINE>
    at <doctest default[2]>:1
    -------------------------
    Called:
      mock(3.14)
    Expected (any of):
      mock(Type(int) | Regex(LOWER_ASCII))

In the last line we've called our mock with float number which is neither
integer, nor lower ASCII string. And since it did not matched our
expectation, :exc:`mockify.exc.UnexpectedCall` was raised - the same that
would be raised if we had used fixed values in expectation.

And now let's try with one more example.

This time we are expecting only positive integer numbers. To expect that we
can combine previously introduced ``Type`` matcher with
:class:`mockify.matchers.Func` matcher. The latter is very powerful, as it
accepts any custom function. Here's our expectation:

.. testcode::

    from mockify.mock import Mock
    from mockify.actions import Return
    from mockify.matchers import Type, Func

    mock = Mock('mock')
    mock.\
        expect_call(Type(int) & Func(lambda x: x > 0, 'POSITIVE_ONLY')).\
        will_repeatedly(Return(True))

And now let's do some checks:

.. doctest::

    >>> mock(1)
    True
    >>> mock(10)
    True
    >>> mock(3.14)
    Traceback (most recent call last):
        ...
    mockify.exc.UnexpectedCall: No matching expectations found for call:
    <BLANKLINE>
    at <doctest default[2]>:1
    -------------------------
    Called:
      mock(3.14)
    Expected (any of):
      mock(Type(int) & Func(POSITIVE_ONLY))

Using matchers in structured data
---------------------------------

You are not only limited to use matchers in ``expect_call()`` arguments and
keyword arguments. You can also use it inside larger structures, like dicts.
That is a side effect of the fact that matchers are implemented by
customizing standard Python's ``__eq__()`` operator, which is called every
time you compare one object with another. Here's an example:

.. testcode::

    from mockify.mock import Mock
    from mockify.actions import Return
    from mockify.matchers import Type, List

    mock = Mock('mock')
    mock.expect_call({
        'action': Type(str),
        'params': List(Type(int), min_length=2),
    }).will_repeatedly(Return(True))

We've recorded expectation that ``mock()`` will be called with dict
containing *action* key that is a string, and *params* key that is a list of
integers containing at least 2 elements. Here's how it works:

.. doctest::

    >>> mock({'action': 'sum', 'params': [2, 3]})
    True
    >>> mock({'action': 'sum', 'params': [2, 3, 4]})
    True
    >>> mock({'action': 'sum', 'params': [2]})
    Traceback (most recent call last):
        ...
    mockify.exc.UnexpectedCall: No matching expectations found for call:
    <BLANKLINE>
    at <doctest default[2]>:1
    -------------------------
    Called:
      mock({'action': 'sum', 'params': [2]})
    Expected (any of):
      mock({'action': Type(str), 'params': List(Type(int), min_length=2)})

In the last example we got :exc:`mockify.exc.UnexpectedCall` exception
because our *params* key got only one argument, while it was expected at
least 2 to be given. There is no limit of how deep you can go with your
structures.

Using matchers in custom objects
--------------------------------

You can also use matchers with your objects. Like in this example:

.. testcode::

    from collections import namedtuple

    from mockify.mock import Mock
    from mockify.matchers import Type

    Vec2 = namedtuple('Vec2', 'x, y')  # (1)

    Float = Type(float)  # (2)

    canvas = Mock('canvas')
    canvas.draw_line.expect_call(
        Vec2(Float, Float), Vec2(Float, Float)).\
        will_repeatedly(Return(True))  # (3)

We've created a vector object (1), then an alias to ``Type(float)`` (2) for a
more readable expectation composing (an ``_`` alias for
:class:`mockify.matchers.Any` is created in same way). Finally, we've created
*canvas* mock and mocked ``draw_line()`` method, taking start and end point
arguments in form of 2-dimensional vectors. And here's how it works:

.. doctest::

    >>> canvas.draw_line(Vec2(0.0, 0.0), Vec2(5.0, 5.0))
    True
    >>> canvas.draw_line(Vec2(0, 0), Vec2(5, 5))
    Traceback (most recent call last):
        ...
    mockify.exc.UnexpectedCall: No matching expectations found for call:
    <BLANKLINE>
    at <doctest default[1]>:1
    -------------------------
    Called:
      canvas.draw_line(Vec2(x=0, y=0), Vec2(x=5, y=5))
    Expected (any of):
      canvas.draw_line(Vec2(x=Type(float), y=Type(float)), Vec2(x=Type(float), y=Type(float)))

Using matchers out of Mockify library
-------------------------------------

Matchers are pretty generic tool that you can also use outside of Mockify -
just for assertion checking. For example, if you have a code that creates
some records with auto increment ID you can use a matcher from Mockify to
check if that ID matches some expected criteria - especially when exact value
is hard to guess:

Here's an example code:

.. testcode::

    import itertools

    _next_id = itertools.count(1)  # This is private

    def make_product(name, description):
        return {
            'id': next(_next_id),
            'name': name,
            'description': description
        }

And here's an example test:

.. testcode::

    from mockify.matchers import Type, Func

    def test_make_product():
        product = make_product('foo', 'foo desc')
        assert product == {
            'id': Type(int) & Func(lambda x: x > 0, 'GREATER_THAN_ZERO'),
            'name' : 'foo',
            'description': 'foo desc',
        }

.. testcode::
    :hide:

    test_make_product()
