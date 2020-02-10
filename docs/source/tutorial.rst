.. ----------------------------------------------------------------------------
.. docs/source/tutorial.rst
..
.. Copyright (C) 2018 - 2020 Maciej Wiatrzyk
..
.. This file is part of Mockify library documentation
.. and is released under the terms of the MIT license:
.. http://opensource.org/licenses/mit-license.php.
..
.. See LICENSE for details.
.. ----------------------------------------------------------------------------

Tutorial
========

.. _creating-mocks:

Using **Mock** class
--------------------

Creating mocks
^^^^^^^^^^^^^^

To create a mock, you first need to import :class:`mockify.mock.Mock` class:

.. testcode::

    from mockify.mock import Mock

Now you have to instantiate previously imported class for every mock you
need. To do that, you simply need to choose a name for each of your mocks,
and then create instances like in this example:

.. testcode::

    foo = Mock('foo')

The rule of thumb says that mock's name should be the same as variable mock
object is assigned to. You can only use names that are valid Python
identifiers or module names. If you give an invalid name, :exc:`TypeError`
will be raised:

.. doctest::

    >>> Mock(123)
    Traceback (most recent call last):
        ...
    TypeError: Mock name must be a valid Python identifier, got 123 instead

Mock objects can automatically create attributes on demand, and that
attributes form **nested mocks** with a root being the one you've created
(which is object *foo* in this example). That makes it possible to call such
mock object for example like this:

.. doctest::

    >>> foo.bar.baz(1, 2)
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: No expectations recorded for mock:
    <BLANKLINE>
    at <doctest default[0]>:1
    -------------------------
    Called:
      foo.bar.baz(1, 2)

In example above, attributes *bar* and *baz* were created automatically. But
since we did not record any expectations, :exc:`mockify.exc.UninterestedCall`
exception was raised. To deal with that you will have to record adequate
expectations.

Using **expect_call()** method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To record expectation, you have to call **expect_call()** method with
exactly the same argument values, argument type and argument count you expect
that given attribute will be called with. For example, to record expectation
for previous example, you will have to write following expectation:

.. testcode::

    foo.bar.baz.expect_call(1, 2)

And now calling that "method" will pass without any exception:

.. testcode::

    foo.bar.baz(1, 2)

That rule applies to any combination of attributes.

Creating ad-hoc data objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can use mock objects to create ad-hoc data objects. Although that may
seem to be a bit overkill, but it may be helpful if you need to return some
data behind a nested attribute, like in this example:

.. doctest::

    >>> obj = Mock('obj')
    >>> obj.foo.bar.baz = 'spam'
    >>> obj.foo.bar.baz
    'spam'

.. _recording-and-validating-expectations:

Recording and validating expectations
-------------------------------------

.. _func-with-out-params:

Mocking functions with output parameters
----------------------------------------

.. _managing-multiple-mocks:

Managing multiple mocks
-----------------------

.. _recording-ordered-expectations:

Recording ordered expectations
------------------------------

.. _setting-expected-call-count:

Setting expected call count
---------------------------

.. _recording-action-chains:

Recording action chains
-----------------------

.. _recording-repeated-actions:

Recording repeated actions
--------------------------

.. _patching-imported-modules:

Patching imported modules
-------------------------

With Mockify you can easily substitute imported module with a mocked version.
Consider following code:

.. testcode::

    import os

    def iter_dirs(path):
        for name in os.listdir(path):
            fullname = os.path.join(path, name)
            if os.path.isdir(fullname):
                yield fullname

That function generates full paths to all direct children directories of
given *path*. And it uses :mod:`os` to make some file system operations. To
test that function without refactoring it you will have to **patch** some
methods of :mod:`os` module. And here's how this can be done in Mockify:

.. testcode::

    from mockify import satisfied, patched
    from mockify.mock import Mock
    from mockify.actions import Return

    def test_iter_dirs():
        os = Mock('os')  # (1)
        os.listdir.expect_call('/tmp').will_once(Return(['foo', 'bar', 'baz.txt']))  # (2)
        os.path.isdir.expect_call('/tmp/foo').will_once(Return(True))  # (3)
        os.path.isdir.expect_call('/tmp/bar').will_once(Return(True))
        os.path.isdir.expect_call('/tmp/baz.txt').will_once(Return(False))

        with patched(os):  # (4)
            with satisfied(os):  # (5)
                assert list(iter_dirs('/tmp')) == ['/tmp/foo', '/tmp/bar']  # (6)

.. testcode::
    :hide:

    test_iter_dirs()

And here's what's going on in presented test:

* We've created *os* mock (1) for mocking **os.listdir()** (2) and
  **os.path.isdir()** (3) methods,
* Then we've used :func:`mockify.patched` context manager (4) that does the
  whole magic of substituting modules matching full names of mocks with
  expectations recorded (which are ``'os.listdir'`` and ``'os.path.isdir'``
  in our case) with corresponding mock objects
* Finally, we've used :func:`mockify.satisfied` context manager (5) to ensure
  that all expectations are satisfied, and ran tested function (6) checking
  it's result.

Note that we did not mock :func:`os.path.join` - that will be used from
:mod:`os` module.
