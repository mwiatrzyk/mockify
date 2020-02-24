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

About Mockify
-------------

Mockify is a highly customizable and expressive mocking library for Python
inspired by Google Mock C++ framework, but adopted to Python world.

Unlike tools like :mod:`unittest.mock`, Mockify is based on **expectations**
that you record on your mocks **before** they are injected to code being
under test. Each expectation represents arguments the mock is expected to be
called with and provides sequence of **actions** the mock will do when called
with that arguments. Actions allow to set a value to be returned, exception
to be raised or just function to be called. Alternatively, if no actions
should take place, you can just say how many times the mock is expected to be
called. And all of these is provided by simple, expressive and easy to use
API.

Here's a simple example:

.. testcode::

    from mockify import satisfied
    from mockify.mock import Mock
    from mockify.actions import Return

    def invoke(func):
        return func()

    def test_invoke_calls_func_returning_hello_world():
        func = Mock('func')
        func.expect_call().will_once(Return('Hello, world!'))

        with satisfied(func):
            assert invoke(func) == 'Hello, world!'

.. testcleanup::

    test_invoke_calls_func_returning_hello_world()

I hope you'll find this library useful.

User's Guide
------------

.. toctree::
    :maxdepth: 3

    installation
    quickstart
    tutorial
    tips-and-tricks
    api
    changelog
    license
