# ---------------------------------------------------------------------------
# mockify/matchers.py
#
# Copyright (C) 2018 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------

"""Module containing predefined matchers.

A matcher is every class that implements following interface:

    ``__repr__(self)``
        Return matcher's text representation.

    ``__eq__(self, other)``
        Check if ``self`` is *equal* to ``other``.

        Here we use standard Python ``__eq__`` operator as it will be
        automatically executed by Python no matter where the matcher is used.
        But *equality* definition is completely up to the matcher
        implementation.

    ``__ne__(self, other)``
        Should be implemented simply like::

            def __ne__(self, other):
                return not self.__eq__(other)
"""


class Any:
    """Matcher that matches any value.

    It is available also as ``_`` (underscore) single instance that can be
    imported from this module.

    For example, you can record expectation that mock must be called with one
    positional argument of any value but exactly 3 times:

        >>> from mockify.matchers import _
        >>> from mockify.mock.function import Function
        >>> foo = Function('foo')
        >>> foo.expect_call(_).times(3)
        <mockify.Expectation: foo(_)>
        >>> for i in range(3):
        ...     foo(i)
        >>> foo.assert_satisfied()
    """

    def __repr__(self):
        return "_"

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


_ = Any()
