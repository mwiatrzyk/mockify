"""A proxy module for making single line import statements.

This module automatically imports public names from other Mockify's modules, so
your imports can now be optionally made in a form of one line statement like
this one:

.. testcode::

    from mockify.api import satisfied, Mock, Return

instead of multiline imports like this one:

.. testcode::

    from mockify.core import satisfied
    from mockify.mock import Mock
    from mockify.actions import Return

This module does not deprecate imports from other public modules - these are
still part of Mockify's public API and there are no plans to change this, so
you are free to use multiline imports if you prefer.

.. note::

    Rationale behind this module is that testing frameworks like PyTest provide
    access to all public names basically via single import, so test helper like
    Mockify should also provide similar behaviour.

.. versionadded:: 0.13
"""

from mockify.core import ordered, satisfied, assert_satisfied, Session
from mockify.mock import ABCMock, Mock, FunctionMock, MockFactory, ObjectMock
from mockify.actions import Return, ReturnAsync, Raise, RaiseAsync, Iterate
from mockify.expect import expect_call
from mockify.cardinality import Exactly, AtLeast, AtMost, Between
from mockify.matchers import _

__all__ = [
    'ordered', 'satisfied', 'assert_satisfied', 'Session', 'ABCMock', 'Mock',
    'FunctionMock', 'MockFactory', 'ObjectMock', 'Return', 'Iterate', 'ReturnAsync', 'Raise',
    'RaiseAsync', 'expect_call', 'Exactly', 'AtLeast', 'AtMost', 'Between', '_'
]
