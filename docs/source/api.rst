API Reference
=============

Mocking frontends
-----------------

Mocking frontends are used to provide easy to use interface on top of classes
from :mod:`mockify.engine` module that act like a backend.

So instead of doing this::

    >>> from mockify.engine import Call, Registry
    >>> reg = Registry()
    >>> reg.expect_call(Call('foo', (1, 2)), 'foo.py', 123)
    <mockify.Expectation: foo(1, 2)>
    >>> reg(Call('foo', (1, 2)))
    >>> reg.assert_satisfied()

You use a frontend to do the same much easier::

    >>> from mockify.mock.function import Function
    >>> foo = Function('foo')
    >>> foo.expect_call(1, 2)
    <mockify.Expectation: foo(1, 2)>
    >>> foo(1, 2)
    >>> foo.assert_satisfied()

``mockify.mock.function`` - Frontends for mocking functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: mockify.mock.function
    :members:
    :show-inheritance:

``mockify.engine`` - Library core
---------------------------------

.. automodule:: mockify.engine
    :members:
    :special-members: __call__
    :show-inheritance:

``mockify.actions`` - Actions for use with *will_once* or *will_repeatedly*
---------------------------------------------------------------------------

.. automodule:: mockify.actions
    :members:
    :show-inheritance:

``mockify.exc`` - Exceptions
----------------------------

.. automodule:: mockify.exc
    :members:
    :show-inheritance:

``mockify.helpers`` - Various helper utilities
----------------------------------------------

.. automodule:: mockify.helpers
    :members:
    :show-inheritance:

``mockify.matchers`` - Matchers for use with *expect_call*
----------------------------------------------------------

.. automodule:: mockify.matchers
    :members:
    :show-inheritance:

``mockify.times`` - Classes for use with *times* method
-------------------------------------------------------

.. automodule:: mockify.times
    :members:
    :special-members: __eq__
    :show-inheritance:
