Quickstart
==========

Introduction
------------

In this quickstart guide you will get familiar with basic concepts of
Mockify by writing example test for simple Python code.

Let's start then!

The **MessageReader** class
---------------------------

We are going to test following Python class:

.. testcode::

    class MessageReader:

        def __init__(self, input_stream):
            self._input_stream = input_stream

        def read(self):
            magic_bytes = self._input_stream.readline()
            if magic_bytes != b'XYZ':
                raise Exception(f"Invalid magic bytes: {magic_bytes!r}")
            message_size = self._input_stream.readline()
            if not message_size.isdigit():
                raise Exception(f"Invalid message size: {message_size!r}")
            return self._input_stream.read(int(message_size)).decode()

This class implements reader of some dummy **XYZ** protocol for transferring
textual messages of known size over some sort of stream. Each message of that
protocol is textual and contains following ``\n``-separated parts::

    MAGIC_BYTES | len(PAYLOAD) | PAYLOAD

Where:

``MAGIC_BYTES``
    Usually every protocol has some magic string that identifies it. For HTTP
    it is simply **HTTP**. For our dummy XYZ protocol it is **XYZ**.

``len(PAYLOAD)``
    Number of ``PAYLOAD`` characters.

``PAYLOAD``
    The body of single XYZ message.

Also notice that that ``MessageReader`` class contains only message decoding
logic, while connection details are hidden behind input stream interface that
is given as a dependency. And that is what we're going to mock.

Creating a mock of **InputStream** interface
--------------------------------------------

To create a mock, you have to import :class:`mockify.mock.Mock` class:

.. testcode::

    from mockify.mock import Mock

And then instantiate it, giving it a name:

.. testcode::

    input_stream = Mock('input_stream')

.. note::
    The rule of thumb is to name your mocks using the same name as variable
    it is assigned to. That name is used when Mockify reports errors and it
    will be easier for you to debug if you follow that rule. The other thing
    is that you can **only** use names that are **valid Python identifiers**.
    That check was added to even enforce previous rule.

We have just created our first mock in Mockify. And for the code we want to
test it is the only one we need. Now we can instantiate ``MessageReader``
class using our newly created mock as an argument:

.. testcode::

    message_reader = MessageReader(input_stream)

Of course nothing interesting has happened inside the constructor, but if you
now call ``read()`` method, the call will fail with
:exc:`mockify.exc.UninterestedCall` exception:

.. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> message_reader.read()
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: No expectations recorded for mock:
    <BLANKLINE>
    at <doctest default[0]>:7
    -------------------------
    Called:
      input_stream.readline()
    Expected:
      no expectations recorded

The error states that the reason of failure was unexpected call of ``read()``
method. That's it - in Mockify we need to first record **expectation** on a mock
**before** it gets called. Otherwise that error will be reported and test will
be terminated. If the error occurs you have to check if that's a missing
expectation, or call to a method that should not take place. In our case we
need to record expectation.

Recording expectations
----------------------

To record expectation on a mock you need to call mock's ``expect_call()``
method that creates and returns :class:`mockify.Expectation` objects. That
method however must be prefixed with a path that leads to a method that is
expected to be called. You also need to know how many times the mock is
expected to be called and what it should do once called.

In our case, we need ``input_stream.readline()`` method to be called **once
without params** and to **return** XYZ protocol's **magic bytes**. Therefore
we need to record expectation that:

* will be expected to be called once,
* will return ``b'XYZ'`` when called.

Recording such expectation in Mockify is very easy:

.. testcode::

    from mockify.actions import Return

    input_stream.readline.expect_call().will_once(Return(b'XYZ'))

We've used ``will_once()`` method to set a **return action** to be executed
once.

.. note::
    You will find more actions in :mod:`mockify.actions` module.

And if we now call ``message_reader.read()``, the call will fail again, but
with :exc:`mockify.exc.OversaturatedCall` exception this time:

.. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> message_reader.read()
    Traceback (most recent call last):
        ...
    mockify.exc.OversaturatedCall: Following expectation was oversaturated:
    <BLANKLINE>
    at <doctest default[0]>:3
    -------------------------
    Pattern:
      input_stream.readline()
    Expected:
      to be called once
    Actual:
      oversaturated by input_stream.readline() at <doctest default[0]>:10 (no more actions)

This kind of exception is raised when actions are recorded on a mock, but it
gets called more times than expected. This behavior is intentional, because a
mock that needs to return a value (in this case) will most likely cause code
being tested to fail if no value is returned. And that could potentially be
harder to investigate than special error reported by Mockify.

To fix that we have to record two expectations, as ``MessageReader`` will
call ``readline()`` twice: once for getting magic bytes, and once for getting
payload size:

.. testcode::

    input_stream.readline.expect_call().will_once(Return(b'XYZ'))
    input_stream.readline.expect_call().will_once(Return(b'13'))

If we now call ``message_reader.read()`` again, it will no longer report
problems with ``readline()`` method. However, it will fail with uninterested
call error one more time:

.. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> message_reader.read()
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: No expectations recorded for mock:
    <BLANKLINE>
    at <doctest default[0]>:13
    --------------------------
    Called:
      input_stream.read(13)
    Expected:
      no expectations recorded

This is the last call to mocked interface - reading message payload. Notice,
that ``input_stream.read(13)`` is now called, and it is called with parameter
this time - payload size that we have injected to the code thanks to our
previous expectation.

Okay, so let's record our final expectation:

.. testcode::

    input_stream.readline.expect_call().will_once(Return(b'XYZ'))
    input_stream.readline.expect_call().will_once(Return(b'13'))
    input_stream.read.expect_call(13).will_once(Return(b'Hello, world!'))

And this time the code will execute fine and return what we have told the
mock to return:

.. doctest::

    >>> message_reader.read()
    'Hello, world!'

.. note::
    This **fast fail** feature of Mockify may be helpful for writing tests
    for legacy code that has no tests. You just create and inject mock, run
    test, see where it failed, record necessary expectation, run again and so
    on.

Verifying expectations
----------------------

In previous example we've managed our tested method to run successfully.
However, we did not verify everything. Notice that all errors Mockify
reported so far were raised **during execution** of tested code. But what
will happen if tested code is broken and some expectations will never get
called or will get called less times than expected?

When test is done, every recorded expectation should be **satisfied** (i.e.
called expected number of times). And we need an assertion to verify that.
For the purpose of this example we can use :func:`mockify.satisfied` context
manager. Here's almost complete solution:

.. testcode::

    from mockify import satisfied

    input_stream.readline.expect_call().will_once(Return(b'XYZ'))
    input_stream.readline.expect_call().will_once(Return(b'13'))
    input_stream.read.expect_call(13).will_once(Return(b'Hello, world!'))

    with satisfied(input_stream):
        assert message_reader.read() == 'Hello, world!'

Context manager we've used accepts mock objects as arguments (you can give
more than one) and checks if every expectation recorded for each of these
mocks is satisfied when scope is left. Besides, use of this context manager
also emphasizes part of test code where unit under test is actually being
executed.

Putting it all together
-----------------------

Finally, let's put it all together into a single working example:

.. testcode:: summary

    from mockify import satisfied
    from mockify.mock import Mock
    from mockify.actions import Return

    class MessageReader:

        def __init__(self, input_stream):
            self._input_stream = input_stream

        def read(self):
            magic_bytes = self._input_stream.readline()
            if magic_bytes != b'XYZ':
                raise Exception(f"Invalid magic bytes: {magic_bytes!r}")
            message_size = self._input_stream.readline()
            if not message_size.isdigit():
                raise Exception(f"Invalid message size: {message_size!r}")
            return self._input_stream.read(int(message_size)).decode()

    def test_read_single_message_from_input_stream():
        # 1. Creating mocks and unit under test
        input_stream = Mock('input_stream')
        message_reader = MessageReader(input_stream)

        # 2. Recording expectations
        input_stream.readline.expect_call().will_once(Return(b'XYZ'))
        input_stream.readline.expect_call().will_once(Return(b'13'))
        input_stream.read.expect_call(13).will_once(Return(b'Hello, world!'))

        # 3. Running unit under test with expectations check
        with satisfied(input_stream):
            assert message_reader.read() == 'Hello, world!'

.. testcleanup:: summary

    test_read_single_message_from_input_stream()

Now we have our first test ready. Notice that it is composed of three major
parts:

* creating mocks and injecting into unit under test,
* recording expectations,
* and running unit under test.

And that structure will most likely become a backbone also for your tests. Of
course you can use helper methods for creating mocks or recording
expectations, but in general the structure of the test will remain the same.

Summary
-------

In this quickstart guide you've learned basic concepts of Mockify. You know
how to create mocks, how to record basic expectations and how to verify if
expectations are satisfied. Now you can start using Mockify in your tests.
But if you want to learn more, please proceed to :ref:`Tutorial` section that
will explain each aspect of Mockify in more detailed form.
