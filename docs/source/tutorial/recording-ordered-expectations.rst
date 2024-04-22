.. ----------------------------------------------------------------------------
.. docs/source/tutorial/recording-ordered-expectations.rst
..
.. Copyright (C) 2019 - 2024 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
..
.. This file is part of Mockify library documentation
.. and is released under the terms of the MIT license:
.. http://opensource.org/licenses/mit-license.php.
..
.. See LICENSE for details.
.. ----------------------------------------------------------------------------
.. _recording-ordered-expectations:

Recording ordered expectations
==============================

.. versionadded:: 0.6

Mockify provides a mechanism for recording **ordered expectation**, i.e.
expectations that can only be resolved in their declaration order. That may
be crucial if you need to provide additional level of testing for parts of
code that **must not** call given interfaces in any order. Consider this:

.. testcode::

    class InterfaceCaller:

        def __init__(self, first, second):
            self._first = first
            self._second = second

        def run(self):
            # A lot of complex processing goes in here...
            self._first.inform()  # (1)
            # ...and some in here.
            self._second.inform()  # (2)

We have a class that depends on two interfaces: *first* and *second*. That
class has a ``run()`` method in which some complex processing takes place.
The result of processing is a **call** to both of these two interfaces, but
**the order does matter**; calling *second* before *first* is considered a
**bug** which should be discovered by tests. And here is our test:

.. testcode::

    from mockify.core import satisfied
    from mockify.mock import Mock

    def test_interface_caller():
        first = Mock('first')
        second = Mock('second')

        first.inform.expect_call()
        second.inform.expect_call()

        caller = InterfaceCaller(first, second)
        with satisfied(first, second):
            caller.run()

.. testcode::
    :hide:

    test_interface_caller()

And of course, the test passes. But will it pass if we change the order of
calls in class we are testing? Of course it **will**, because by default the
order of declared expectations is irrelevant (for as long as return values
does not come into play). And here comes **ordered expectations**:

.. testcode::
    :hide:

    class InterfaceCaller:

        def __init__(self, first, second):
            self._first = first
            self._second = second

        def run(self):
            # A lot of complex processing goes in here...
            self._second.inform()  # (2)
            # ...and some in here.
            self._first.inform()  # (1)

.. testcode::
    :hide:

    test_interface_caller()

.. testcode::

    from mockify.core import satisfied, ordered
    from mockify.mock import MockFactory

    def test_interface_caller():
        factory = MockFactory()  # (1)
        first = factory.mock('first')
        second = factory.mock('second')

        first.inform.expect_call()
        second.inform.expect_call()

        caller = InterfaceCaller(first, second)
        with satisfied(factory):
            with ordered(factory):  # (2)
                caller.run()

In the test above we've used mock factory (1), because ordered expectations
require all checked mocks to operate on a common session. The main difference
however is use of :func:`mockify.core.ordered` context manager (2) which ensures that
given mocks (mocks created by *factory* in this case) will be called **in
their declaration order**. And since we've changed the order in tested code,
the test will no longer pass and :exc:`mockify.exc.UnexpectedCallOrder`
assertion will be raised:

.. doctest::

    >>> test_interface_caller()
    Traceback (most recent call last):
        ...
    mockify.exc.UnexpectedCallOrder: Another mock is expected to be called:
    <BLANKLINE>
    at <doctest default[0]>:9
    -------------------------
    Called:
      second.inform()
    Expected:
      first.inform()

And that exception tells us that we've called ``second.inform()``, while it
was expected to call ``first.inform()`` earlier.
