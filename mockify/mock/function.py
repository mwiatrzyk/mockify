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
    """Mock class that is used to mock standalone Python functions.

    This class is basically a frontend on top of
    :class:`mockify.engine.Registry` object, as it forwards all method calls
    towards default created or custom registry object.

    Each instance of this class represents single mock function of predefined
    name. Such function can be then used as a callback or injected in any other
    way to the code being under test.

    Mock functions can be created using following boilerplate pattern:

        >>> foo = Function('foo')
        >>> foo
        <mockify.mock.Function('foo')>

    It is recommended for mock's name to be the same as attribute name mock
    object is assigned to.

    Once mock function object is created, you can record expectations. This
    procedure can be done after injection of those mock function into code
    under test, but must be done before that code gets executed. For example,
    if you expect ``foo`` to be called twice with ``(1, 2)`` as positional
    arguments, you would record following expectations:

        >>> foo.expect_call(1, 2).times(2)
        <mockify.Expectation(foo(1, 2))>

    To check if mock function has all expectations satisfied, you will use
    :meth:`assert_satisfied` method. Since mock was not called yet,
    ``assert_satisfied`` will fail:

        >>> foo.assert_satisfied()
        Traceback (most recent call last):
            ...
        mockify.exc.Unsatisfied: following 1 expectation(-s) are not satisfied:
        <BLANKLINE>
        at <doctest mockify.mock.function.Function[2]>:1
        ------------------------------------------------
            Pattern: foo(1, 2)
           Expected: to be called twice
             Actual: never called

    But if ``foo`` is now calle expected number of times (no less, no more) -
    then ``assert_satisfied`` will pass:

        >>> foo(1, 2)
        >>> foo(1, 2)
        >>> foo.assert_satisfied()

    Usually, you'll be dealing with more that just a one mock function in your
    tests. To avoid calling ``assert_satisfied`` several times (each for
    different mock object), you can create your own registry and pass it to all
    function mocks that are created. For example:

        >>> from mockify.engine import Registry
        >>> reg = Registry()
        >>> foo = Function('foo', reg)
        >>> bar = Function('bar', reg)
        >>> foo.expect_call()
        <mockify.Expectation(foo())>
        >>> bar.expect_call()
        <mockify.Expectation(bar())>

    Now you can use one single call to see that two expectations are not
    satisfied:

        >>> reg.assert_satisfied()
        Traceback (most recent call last):
            ...
        mockify.exc.Unsatisfied: following 2 expectation(-s) are not satisfied:
        <BLANKLINE>
        at <doctest mockify.mock.function.Function[11]>:1
        -------------------------------------------------
            Pattern: foo()
           Expected: to be called once
             Actual: never called
        <BLANKLINE>
        at <doctest mockify.mock.function.Function[12]>:1
        -------------------------------------------------
            Pattern: bar()
           Expected: to be called once
             Actual: never called

    And when you call that mock functions, registry will be satisfied:

        >>> foo()
        >>> bar()
        >>> reg.assert_satisfied()

    :param name:
        Mock function name

    :param registry:
        Instance of :class:`mockify.engine.Registry` class representing
        expectation registry.

        This can be shared between multiple mock functions.
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

        This method returns :class:`mockify.engine.Expectation` object that can
        be used to record more sophisticated behaviors.

        See :meth:`mockify.engine.Registry.expect_call` for more information.
        """
        call = Call(self._name, args or None, kwargs or None)
        filename, lineno = _utils.extract_filename_and_lineno_from_stack(-1)
        return self._registry.expect_call(call, filename, lineno)

    def assert_unsatisfied(self):
        """Assert that this function mock is unsatisfied.

        If mock is already satisfied, then
        :exc:`mockify.exc.Satisfied` will be raised.

        See :meth:`mockify.engine.Registry.assert_unsatisfied` for more
        information.
        """
        self._registry.assert_unsatisfied(self._name)

    def assert_satisfied(self):
        """Assert that this function mock is satisfied.

        If mock is not satisfied, then :exc:`mockify.exc.Unsatisfied`
        will be raised.

        See :meth:`mockify.engine.Registry.assert_satisfied` for more
        information.
        """
        self._registry.assert_satisfied(self._name)
