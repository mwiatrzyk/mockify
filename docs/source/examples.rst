Examples
========

Testing simple ``EventLoop`` class
----------------------------------

In this example, you'll learn of how to use ``FunctionMock`` class to test some
simple ``EventLoop`` class.

Here's the code of ``EventLoop`` class::

    >>> import functools
    >>> import collections

    >>> class EventLoop:
    ...
    ...     def __init__(self):
    ...         self._callbacks = collections.deque()
    ...
    ...     def call_soon(self, callback, *args, **kwargs):
    ...         self._callbacks.append(
    ...             functools.partial(callback, *args, **kwargs))
    ...
    ...     def run(self):
    ...         while self._callbacks:
    ...             callback = self._callbacks.popleft()
    ...             callback()

Basically, it has ``call_soon`` method for scheduling execution of some
callback function, and a ``run`` method for running all scheduled callback
methods. Each new callback is added to the end of a queue, and a ``run`` method
pops callback from queue's front, invokes it and loops until there are
callbacks in the queue. Each executed callback can add more callbacks and so
on.

Let's now create a test that tests if added callback is executed once with
given params after ``run`` method is called.

Without any mocking library, the test would possibly look like this::

    >>> def test_callback_is_executed_after_run_is_called__1():
    ...
    ...     def callback(*args, **kwargs):
    ...         called.append((args, kwargs))
    ...
    ...     called = []
    ...
    ...     uut = EventLoop()
    ...     uut.call_soon(callback, 1, 2, c=3)
    ...
    ...     assert not called
    ...
    ...     uut.run()
    ...
    ...     assert len(called) == 1
    ...     assert called[0] == ((1, 2), {'c': 3})

The same using Mockify would look like this::

    >>> from mockify.mock import FunctionMock

    >>> def test_callback_is_executed_after_run_is_called__2():
    ...     callback = FunctionMock('callback')
    ...     callback.expect_call(1, 2, c=3)
    ...
    ...     uut = EventLoop()
    ...     uut.call_soon(callback, 1, 2, c=3)
    ...
    ...     callback.assert_not_satisfied()
    ...
    ...     uut.run()
    ...
    ...     callback.assert_satisfied()

Or even more clean if ``assert_satisfied`` context manager is used::

    >>> from mockify import assert_satisfied
    >>> from mockify.mock import FunctionMock

    >>> def test_callback_is_executed_after_run_is_called__3():
    ...     callback = FunctionMock('callback')
    ...     callback.expect_call(1, 2, c=3)
    ...
    ...     uut = EventLoop()
    ...     uut.call_soon(callback, 1, 2, c=3)
    ...
    ...     with assert_satisfied(callback):
    ...         uut.run()

Let's now execute those tests to check if they are passing::

    >>> test_callback_is_executed_after_run_is_called__1()
    >>> test_callback_is_executed_after_run_is_called__2()
    >>> test_callback_is_executed_after_run_is_called__3()
