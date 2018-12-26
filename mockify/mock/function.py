# ---------------------------------------------------------------------------
# mockify/mock.py
#
# Copyright (C) 2018 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------

from mockify import _utils
from mockify.engine import Call, Registry


class Function:
    """Class for mocking Python functions.

    Example usage:

        >>> foo = Function('foo')
        >>> foo.expect_call(1, 2).times(2)
        <mockify.Expectation: foo(1, 2)>
        >>> for _ in range(2):
        ...     foo(1, 2)
        >>> foo.assert_satisfied()

    :param name:
        Mock function name

    :param registry:
        This is optional.

        Use this to pass custom instance of :class:`mockify.engine.Registry`
        class if you need to share it between multiple frontends. Sharing is
        useful for example to check if all mocks are satisfied using one
        ``assert_satisfied`` call:

            >>> from mockify.engine import Registry
            >>> reg = Registry()
            >>> foo = Function('foo', registry=reg)
            >>> bar = Function('bar', registry=reg)
            >>> foo.expect_call()
            <mockify.Expectation: foo()>
            >>> bar.expect_call()
            <mockify.Expectation: bar()>
            >>> foo()
            >>> bar()
            >>> reg.assert_satisfied()
    """

    def __init__(self, name, registry=None):
        self._name = name
        self._registry = registry or Registry()

    def __repr__(self):
        return "<mockify.mock.{}({!r})>".format(self.__class__.__name__, self._name)

    def __call__(self, *args, **kwargs):
        return self._registry(
            Call(self._name, args or None, kwargs or None))

    def expect_call(self, *args, **kwargs):
        """Record call expectation.

        This method creates :class:`mockify.engine.Call` instance giving it
        ``args`` and ``kwargs``, fetches file and line number from current call
        stack and triggers :meth:`mockify.engine.Registry.expect_call` and
        returns expectation object it produces.
        """
        call = Call(self._name, args or None, kwargs or None)
        filename, lineno = _utils.extract_filename_and_lineno_from_stack(-1)
        return self._registry.expect_call(call, filename, lineno)

    def assert_satisfied(self):
        """Assert that this function mock is satisfied.

        This method just calls :meth:`mockify.engine.Registry.assert_satisfied`
        with ``name`` given via constructor as an argument.
        """
        self._registry.assert_satisfied(self._name)
