"""Classes for mocking things.

For convenience, following most frequently used classes are available
directly from this module:

    * :class:`mockify.mock.object.Object`
    * :class:`mockify.mock.function.Function`
    * :class:`mockify.mock.function.FunctionFactory`

So you can just write::

    >>> from mockify.mock import Object, Function, FunctionFactory
"""

from .object import Object
from .function import Function, FunctionFactory
