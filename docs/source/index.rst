.. ----------------------------------------------------------------------------
.. docs/source/index.rst
..
.. Copyright (C) 2018 - 2020 Maciej Wiatrzyk
..
.. This file is part of Mockify library documentation
.. and is released under the terms of the MIT license:
.. http://opensource.org/licenses/mit-license.php.
..
.. See LICENSE for details.
.. ----------------------------------------------------------------------------
.. Mockify documentation master file, created by
   sphinx-quickstart on Fri Nov  9 08:43:36 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Mockify!
===================

Welcome to Mockify library documentation!

Mockify is a mocking toolkit for Python that follows principles originally
introduced by Google Mock C++ mocking framework, but adapted to Python world.
With Mockify you can create clean, expressive, easy to understand and highly
customizable mocks or stubs for your tests.

With Mockify you record **expectations** that are consumed during test
execution. Expectations tell the mock what it should do once called with
given arguments and how many times it is expected to be called. Finally, at
the end of your test, you just check if all expectations are **satisfied**.

Here's an example:

.. testcode::

    from mockify import assert_satisfied
    from mockify.mock import Function
    from mockify.actions import Return


    class Greeter:

        def __init__(self, name_getter):
            self._name_getter = name_getter

        def greet(self):
            return 'Hello, ' + self._name_getter() + '!'


    def test_greeter():
        name_getter = Function('name_getter')

        name_getter.expect_call().will_once(Return('John'))

        greeter = Greeter(name_getter)
        with assert_satisfied(name_getter):
            assert greeter.greet() == 'Hello, John!'

.. testcleanup::

    test_greeter()

Mockify allows you to create mocks that:

    * Can be called with any number and kind of arguments
    * Can have maximal, minimal or exact expected call count set
    * Can be expected to be never called
    * Can use **matchers** whenever you don't know or don't need exact argument
      values the mock will be called with
    * Can use matchers inside Python collections like dicts, lists etc. to
      ignore certain keys or items
    * Can have **action chains** recorded, so every new call consumes another
      action from the chain, and each action can be different
    * Can have **repeated actions** recorded, so you will be able to set one
      action that is executed on every mock call
    * Can pass all arguments to actions, so you are able to do basically
      anything when the mock is called

User's Guide
------------

.. toctree::
   :maxdepth: 3

   installation
   quickstart
   tutorial
   api
   changelog
   license
