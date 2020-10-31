.. ----------------------------------------------------------------------------
.. docs/source/quickstart.rst
..
.. Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
..
.. This file is part of Mockify library documentation
.. and is released under the terms of the MIT license:
.. http://opensource.org/licenses/mit-license.php.
..
.. See LICENSE for details.
.. ----------------------------------------------------------------------------

Quickstart
==========

Introduction
------------

In this quickstart guide we are going to use test-driven development
technique to write a class for parsing messages of some textual protocol for
transferring bytes of data of known size. In this guide you will:

* get familiar with basic concepts of Mockify,
* learn how to create **mocks** and inject them to code being under test,
* learn how to record **expectations** and **actions** on that mocks,
* learn how to set expected call count on mocks,
* learn how to check if mocks were **satisfied** once test is ended,
* learn how to read some of Mockify assertions.

After going through this quickstart guide you will be able to use Mockify in
your projects, but to learn even more you should also read :ref:`Tutorial`
chapter, which covers some more advanced features. I hope you will enjoy
Mockify.

Let's start then!

The **XYZ** protocol
--------------------

Imagine you work in a team which was given a task to design and write a
library for transferring binary data over a wire between two peers. There are
no any special requirements for chunking data, re-sending chunks, handling
connection failures etc. The protocol must be very simple, easy to implement
in different languages, which other teams will start implementing once design
is done, and easy to extend in the future if needed. Moreover, there is a
preference for this protocol to be textual, like HTTP. So your team starts
with a brainstorming session and came out with following protocol design
proposal::

    MAGIC_BYTES | \n | Version | \n | len(PAYLOAD) | \n | PAYLOAD

The protocol was named **XYZ** and single message of the protocol is composed
of following parts, separated with single newline character:

``MAGIC_BYTES``
    The string ``"XYZ"`` with protocol name.

    Used to identify beginning of **XYZ** messages in byte stream coming from
    remote peer.

``Version``
    Protocol version in string format.

    Currently always ``"1.0"``, but your team wants the protocol to be
    extensible in case when more features would have to be incorporated.

``len(PAYLOAD)``
    Length of ``PAYLOAD`` part in bytes, represented in string format.

``PAYLOAD``
    Message payload.

    These are actual bytes that are transferred.

You and your team have presented that design to other teams, the design was
accepted, and now every team starts implementing the protocol. Your team is
responsible for Python part.

The **XYZReader** class
-----------------------

Your team has decided to divide work into following independent flows:

* Implementing higher level **StreamReader** and **StreamWriter** classes for
  reading/writing bytes from/to underlying socket, but with few additional
  features like reading/writing **exactly** given amount of bytes (socket on
  its own does not guarantee that),
* Implementing protocol **logic** in form of **XYZReader** and
  **XYZWriter** classes that depend on stream readers and writers,
  accordingly.

The only common point between these two categories of classes is the
interface between protocol logic and streams. After internal discussion you
and your team agreed for following interfaces::

    class StreamReader:

        def read(self, count) -> bytes
            """Read exactly *count* data from underlying stream."""

        def readline(self) -> bytes
            """Read data from underlying stream and stop once newline is
            found.

            Newline is also returned, as a last byte.
            """

    class StreamWriter:

        def write(self, buffer):
            """Write entire *buffer* to underlying stream."""

Now half of the team can work on implementation of those interfaces, while
the other half - on implementation of protocol's logic. You will be writing
**XYZReader** class.

Writing first test
------------------

Step 0: Mocking **StreamReader** interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You know that **XYZReader** class logic must somehow use **StreamReader**. So
you've started with following draft:

.. testcode::

    class XYZReader:

        def __init__(self, stream_reader):
            self._stream_reader = stream_reader

        def read(self):
            return b'Hello world!'

To instantiate that class you need to pass something as a *stream_reader*
parameter. You know how this interface looks like, but don't have a **real**
implementation, because it is under development by rest of your team. But you
cannot wait until they're done - you have to **mock** it. And here Mockify
comes in to help you.

First you need to import :class:`mockify.mock.Mock` class:

.. testcode::

    from mockify.mock import Mock

This class can be used to mock things like functions, methods, calls via
module, getters, setters and more. This is the only one class to create
mocks. And now you can instantiate it into **StreamReader** mock by creating
instance of **Mock** class giving it a name:

.. testcode::

    stream_reader = Mock('stream_reader')

As you can see, there is no interface defined yet. It will be defined soon.
Now you can instantiate **XYZReader** class with the mock we've created
earlier:

.. testcode::

    xyz_reader = XYZReader(stream_reader)
    assert xyz_reader.read() == b'Hello world!'

And here's complete test at this step:

.. testcode::

    from mockify.mock import Mock

    def test_read_xyz_message():
        stream_reader = Mock('stream_reader')
        xyz_reader = XYZReader(stream_reader)
        assert xyz_reader.read() == b'Hello world!'

.. testcode::
    :hide:

    test_read_xyz_message()

Step 1: Reading magic bytes
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Okay, you have first iteration ready, but in fact there is nothing really
interesting happening yet. Let's now add some business logic. You know, that
first part of **XYZ** message is ``MAGIC_BYTES`` string that should always be
``"XYZ"``. To get first part of message from incoming payload you need to
read it from underlying **StreamReader**. And since we've used
newline-separated parts, we'll be using **readline()** method. Here's
**XYZReader** class supplied with code for reading ``MAGIC_BYTES``:

.. testcode::

    class XYZReader:

        def __init__(self, stream_reader):
            self._stream_reader = stream_reader

        def read(self):
            self._stream_reader.readline()
            return b'Hello world!'

And now let's run our test again. You'll see that it fails with
:exc:`mockify.exc.UninterestedCall` exception:

.. testsetup::

    from mockify.mock import Mock

    def test_read_xyz_message():
        stream_reader = Mock('stream_reader')
        xyz_reader = XYZReader(stream_reader)
        assert xyz_reader.read() == b'Hello world!'

.. doctest::

    >>> test_read_xyz_message()
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: No expectations recorded for mock:
    <BLANKLINE>
    at <doctest default[0]>:7
    -------------------------
    Called:
      stream_reader.readline()

That exception is triggered when for called mock there are no
**expectations** recorded. To make the test pass again you have to record
expectation for **stream_reader.readline()** method on *stream_reader* mock.
Expectations are recorded by calling **expect_call()** method with arguments
(positional and/or keyword) you **expect** your mock to be called with. And
that method has to be called on *readline* attribute of *stream_reader* mock
object. Here's complete solution:

.. testcode::

    from mockify.mock import Mock

    def test_read_xyz_message():
        stream_reader = Mock('stream_reader')
        stream_reader.readline.expect_call()
        xyz_reader = XYZReader(stream_reader)
        assert xyz_reader.read() == b'Hello world!'

.. testcode::
    :hide:

    test_read_xyz_message()

Step 2: Reading version
^^^^^^^^^^^^^^^^^^^^^^^

Now let's go back to out **XYZReader** class and add instruction for reading
``Version`` part of **XYZ** protocol message:

.. testcode::

    class XYZReader:

        def __init__(self, stream_reader):
            self._stream_reader = stream_reader

        def read(self):
            self._stream_reader.readline()  # read magic bytes
            self._stream_reader.readline()  # read version
            return b'Hello world!'

.. testcode::
    :hide:

    test_read_xyz_message()

If you now run the test again, you'll see it passes. That's not what we were
expecting: we've changed the code, so the test should fail. But it doesn't.
And that is due to the fact that we are missing one additional assertion.

Step 3: Using **satisfied()** context manager
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In Mockify not all assertion errors will be caused by invalid or unexpected
mock calls. If the call to mock finds matching expectation, it runs it. And
running expectation can be in some situations as trivial as just increasing
call counter, with no side effects. And that is what happened in previous
test.

To make your test verify all aspects of mocks provided by Mockify, you have
to check if mocks you were created are **satisfied** before your test ends. A
mock is said to be satisfied if all its expectations are consumed during
execution of tested code. Such check can be done in few ways, but this time
let's use :func:`mockify.satisfied` context manager:

.. testcode::

    from mockify import satisfied
    from mockify.mock import Mock

    def test_read_xyz_message():
        stream_reader = Mock('stream_reader')
        stream_reader.readline.expect_call()
        xyz_reader = XYZReader(stream_reader)
        with satisfied(stream_reader):
            assert xyz_reader.read() == b'Hello world!'

This context manager is created with mock object(-s) as argument(-s) and
should wrap part of the test function where tested code is executed. If at
least one of given mocks have at least one expectation **unsatisfied** (i.e.
called less or more times than expected), then context manager fails with
:exc:`mockify.exc.Unsatisfied` assertion. And that happens when our updated
test is run:

.. doctest::

    >>> test_read_xyz_message()
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: Following expectation is not satisfied:
    <BLANKLINE>
    at <doctest default[0]>:6
    -------------------------
    Pattern:
      stream_reader.readline()
    Expected:
      to be called once
    Actual:
      called twice

The error was caused by second call to **stream_reader.readline()** method
(to read protocol version), but we have only one expectation recorded in our
test. This time we know that test should be adjusted, but of course that
could also mean (f.e. when test was passing before making changes) that
tested code needs to be fixed.

Step 4: Using **Expectation.times()** method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Okay, we know that our expectation needs to be somehow extended to fix error
from previous step. We can either double the expectation (i.e. copy and
paste just below) or change expected call count, which is one by default.
Let's go with a second approach.

When you call **expect_call()**, special :class:`mockify.Expectation` object
is created and returned. That object has few methods that can be used to
refine the expectation. And one of these methods is
:meth:`mockify.Expectation.times`. Here's our fixed test with
**stream_reader.readline()** expected to be called twice:

.. testcode::

    from mockify import satisfied
    from mockify.mock import Mock

    def test_read_xyz_message():
        stream_reader = Mock('stream_reader')
        stream_reader.readline.expect_call().times(2)
        xyz_reader = XYZReader(stream_reader)
        with satisfied(stream_reader):
            assert xyz_reader.read() == b'Hello world!'

As you can see, the expectation clearly says that it is expected to be called
twice. And now our test is running fine, so let's go back to **XYZReader**
class, because there are still two parts missing.

.. testcode::
    :hide:

    test_read_xyz_message()

Step 5: Reading payload
^^^^^^^^^^^^^^^^^^^^^^^

So far we've read magic bytes and version of our **XYZ** protocol frame. In
this section let's speed up a bit and read two remaining parts at once:
payload size and payload. Here's updated **XYZReader** class:

.. testcode::

    class XYZReader:

        def __init__(self, stream_reader):
            self._stream_reader = stream_reader

        def read(self):
            self._stream_reader.readline()  # read magic bytes
            self._stream_reader.readline()  # read version
            payload_size = self._stream_reader.readline()  # read payload size (1)
            payload_size = payload_size.rstrip()  # trim ending newline (which is included) (2)
            payload_size = int(payload_size)  # conversion to int (3)
            return self._stream_reader.read(payload_size)  # read payload (4)

Here we are once again calling **readline()** to get payload size as string
ending with newline (1). Then ending newline is stripped (2) and payload size
is converted to integer (3). Finally **read()** method is called, with
calculated *payload_size* as an argument (4).

Now let's try to run our test we fixed before. The test will fail with
following error:

.. doctest::

    >>> test_read_xyz_message()
    Traceback (most recent call last):
        ...
    AttributeError: 'NoneType' object has no attribute 'rstrip'

It fails on (2), during test code execution, not during checking if
expectations are satisfied. This is caused by default value returned by
mocked call, which is ``None`` - like for Python functions that does not
return any values. To make our test move forward we need to change that
default behavior.

Step 6: Introducing **actions**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Mockify provides so called **actions**, available via :mod:`mockify.actions`
module. Actions are simply special classes that are used to override default
behaviour of returning ``None`` when mock is called. You record actions
directly on expectation object using one of two methods:

* :meth:`mockify.Expectation.will_once` for recording chains of unique actions,
* or :meth:`mockify.Expectation.will_repeatedly` for recording so called
  **repeated actions**.

In this example we'll cover use of first of that methods and also we'll use
:class:`mockify.actions.Return` action for setting return value. Here's a
fixed test:

.. testcode::

    from mockify import satisfied
    from mockify.mock import Mock
    from mockify.actions import Return

    def test_read_xyz_message():
        stream_reader = Mock('stream_reader')
        stream_reader.readline.expect_call().times(2)
        stream_reader.readline.expect_call().will_once(Return(b'12\n')) # (1)
        xyz_reader = XYZReader(stream_reader)
        with satisfied(stream_reader):
            assert xyz_reader.read() == b'Hello world!'

We've added one more expectation on **readline()** (1) and recorded single
action to return ``b'12\n'`` as mock's return value. So when **readline()**
is called for the third time, recorded action is invoked, forcing it to
return given bytes. Of course the test will move forward now, but it will
fail again, but few lines later:

.. doctest::

    >>> test_read_xyz_message()
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: No expectations recorded for mock:
    <BLANKLINE>
    at <doctest default[0]>:12
    --------------------------
    Called:
      stream_reader.read(12)

Yes, that's right - we did not record any expectations for **read()** method,
and :exc:`mockify.exc.UninterestedCall` tells that. We need to fix that by
recording adequate expectation.

Step 7: Completing the test
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here's our final complete and passing test with one last missing expectation
recorded:

.. testcode::

    from mockify import satisfied
    from mockify.mock import Mock
    from mockify.actions import Return

    def test_read_xyz_message():
        stream_reader = Mock('stream_reader')
        stream_reader.readline.expect_call().times(2)
        stream_reader.readline.expect_call().will_once(Return(b'12\n')) # (1)
        stream_reader.read.expect_call(12).will_once(Return(b'Hello world!'))  # (2)
        xyz_reader = XYZReader(stream_reader)
        with satisfied(stream_reader):
            assert xyz_reader.read() == b'Hello world!'

.. testcode::
    :hide:

    test_read_xyz_message()

We've added **read()** expectation at (2). Note that this time it is expected
to be called with an argument, which is the same as we've injected in (1),
but converted to integer (as our tested code does).

Verifying magic bytes
---------------------

So far we've written one test covering successful scenario of reading message
from underlying stream. Let's take a look at our **XYZReader** class we've
developed:

.. testcode::

    class XYZReader:

        def __init__(self, stream_reader):
            self._stream_reader = stream_reader

        def read(self):
            self._stream_reader.readline()  # read magic bytes (1)
            self._stream_reader.readline()  # read version (2)
            payload_size = self._stream_reader.readline()
            payload_size = payload_size.rstrip()
            payload_size = int(payload_size)
            return self._stream_reader.read(payload_size)

There are two NOK (not OK) scenarios missing:

    * magic bytes verification (1),
    * and version verification (2).

Let's start by writing test that handles checking if magic bytes received are
equal to ``b"XYZ"``. We've decided to raise **XYZError** exception (not yet
declared) in case when magic bytes are different than expected. Here's the
test:

.. testcode::

    import pytest

    from mockify.mock import Mock
    from mockify.actions import Return

    def test_when_invalid_magic_bytes_received__then_xyz_error_is_raised():
        stream_reader = Mock('stream_reader')
        stream_reader.readline.expect_call().will_once(Return(b'ABC\n'))
        xyz_reader = XYZReader(stream_reader)
        with pytest.raises(XYZError) as excinfo:
            xyz_reader.read()
        assert str(excinfo.value) == "Invalid magic bytes: b'ABC'"

But that test will fail now, because we do not have **XYZError** defined:

.. doctest::

    >>> test_when_invalid_magic_bytes_received__then_xyz_error_is_raised()
    Traceback (most recent call last):
        ...
    NameError: name 'XYZError' is not defined

So let's define it:

.. testcode::

    class XYZError(Exception):
        pass

And if now run the test again, it will fail with
:exc:`mockify.exc.OversaturatedCall` error, because we do not have that
functionality implemented yet:

.. doctest::

    >>> test_when_invalid_magic_bytes_received__then_xyz_error_is_raised()
    Traceback (most recent call last):
        ...
    mockify.exc.OversaturatedCall: Following expectation was oversaturated:
    <BLANKLINE>
    at <doctest default[0]>:8
    -------------------------
    Pattern:
      stream_reader.readline()
    Expected:
      to be called once
    Actual:
      oversaturated by stream_reader.readline() at <doctest default[0]>:8 (no more actions)

Now we need to go back to our **XYZReader** class and fix it by implementing
exception raising when invalid magic bytes are received:

.. testcode::

    class XYZError(Exception):
        pass

    class XYZReader:

        def __init__(self, stream_reader):
            self._stream_reader = stream_reader

        def read(self):
            magic_bytes = self._stream_reader.readline()
            magic_bytes = magic_bytes.rstrip()
            if magic_bytes != b'XYZ':
                raise XYZError("Invalid magic bytes: {!r}".format(magic_bytes))
            self._stream_reader.readline()
            payload_size = self._stream_reader.readline()
            payload_size = payload_size.rstrip()
            payload_size = int(payload_size)
            return self._stream_reader.read(payload_size)

.. testcode::
    :hide:

    test_when_invalid_magic_bytes_received__then_xyz_error_is_raised()

And now our second test will run fine, but first one will fail:

.. doctest::

    >>> test_read_xyz_message()
    Traceback (most recent call last):
        ...
    AttributeError: 'NoneType' object has no attribute 'rstrip'

Let's have a look at our first test again:

.. testcode::

    from mockify import satisfied
    from mockify.mock import Mock
    from mockify.actions import Return

    def test_read_xyz_message():
        stream_reader = Mock('stream_reader')
        stream_reader.readline.expect_call().times(2)  # (1)
        stream_reader.readline.expect_call().will_once(Return(b'12\n'))
        stream_reader.read.expect_call(12).will_once(Return(b'Hello world!'))
        xyz_reader = XYZReader(stream_reader)
        with satisfied(stream_reader):
            assert xyz_reader.read() == b'Hello world!'

As you can see, at (1) we are expecting **readline()** to be called twice,
but we did not provided any value to be returned. And that was fine when we
were implementing OK case, but since we have changed **XYZReader** class, we
need to inject proper magic bytes here. Here's fixed OK case test:

.. testcode::

    from mockify import satisfied
    from mockify.mock import Mock
    from mockify.actions import Return

    def test_read_xyz_message():
        stream_reader = Mock('stream_reader')
        stream_reader.readline.expect_call().will_once(Return(b'XYZ\n'))
        stream_reader.readline.expect_call()
        stream_reader.readline.expect_call().will_once(Return(b'12\n'))
        stream_reader.read.expect_call(12).will_once(Return(b'Hello world!'))
        xyz_reader = XYZReader(stream_reader)
        with satisfied(stream_reader):
            assert xyz_reader.read() == b'Hello world!'

.. testcode::
    :hide:

    test_read_xyz_message()

Verifying version
-----------------

Since third of our tests will be basically written in the same way as second
one, let me just present final solution.

Here's **XYZReader** class with code that verifies version:

.. testcode::

    class XYZError(Exception):
        pass

    class XYZReader:

        def __init__(self, stream_reader):
            self._stream_reader = stream_reader

        def read(self):
            magic_bytes = self._stream_reader.readline()
            magic_bytes = magic_bytes.rstrip()
            if magic_bytes != b'XYZ':
                raise XYZError("Invalid magic bytes: {!r}".format(magic_bytes))
            version = self._stream_reader.readline()
            version = version.rstrip()
            if version != b'1.0':
                raise XYZError("Unsupported version: {!r}".format(version))
            payload_size = self._stream_reader.readline()
            payload_size = payload_size.rstrip()
            payload_size = int(payload_size)
            return self._stream_reader.read(payload_size)

And here's our third test - the one that checks if exception is raised when
invalid version is provided:

.. testcode::

    import pytest

    from mockify.mock import Mock
    from mockify.actions import Return

    def test_when_invalid_version_received__then_xyz_error_is_raised():
        stream_reader = Mock('stream_reader')
        stream_reader.readline.expect_call().will_once(Return(b'XYZ\n')) # (1)
        stream_reader.readline.expect_call().will_once(Return(b'2.0\n')) # (2)
        xyz_reader = XYZReader(stream_reader)
        with pytest.raises(XYZError) as excinfo:
            xyz_reader.read()
        assert str(excinfo.value) == "Unsupported version: b'2.0'"  # (3)

.. testcode::
    :hide:

    test_when_invalid_version_received__then_xyz_error_is_raised()

Here we have two **readline()** expectations recorded. At (1) we've set valid
magic bytes (we are not interested in exception raised at that point), and
then at (2) we've set an unsupported version, causing **XYZError** to be
raised. Finally, at (3) we are checking if valid exception was raised.

Of course we also had to fix our first test again, returning valid version
instead of ``None``:

.. testcode::

    from mockify import satisfied
    from mockify.mock import Mock
    from mockify.actions import Return

    def test_read_xyz_message():
        stream_reader = Mock('stream_reader')
        stream_reader.readline.expect_call().will_once(Return(b'XYZ\n'))
        stream_reader.readline.expect_call().will_once(Return(b'1.0\n'))
        stream_reader.readline.expect_call().will_once(Return(b'12\n'))
        stream_reader.read.expect_call(12).will_once(Return(b'Hello world!'))
        xyz_reader = XYZReader(stream_reader)
        with satisfied(stream_reader):
            assert xyz_reader.read() == b'Hello world!'

.. testcode::
    :hide:

    test_read_xyz_message()

Refactoring tests
-----------------

If you take a look at all three tests at once you'll see a some parts are
basically copied and pasted. Creating *stream_reader* mock, instantiating
**XYZReader** class and checking if mocks are satisfied can be done better if
we use organize our tests with a class:

.. testcode::

    import pytest

    from mockify import assert_satisfied
    from mockify.mock import Mock
    from mockify.actions import Return

    class TestXYZReader:

        def setup_method(self):
            self.stream_reader = Mock('stream_reader')  # (1)
            self.uut = XYZReader(self.stream_reader)  # (2)

        def teardown_method(self):
            assert_satisfied(self.stream_reader)  # (3)

        def test_read_xyz_message(self):
            self.stream_reader.readline.expect_call().will_once(Return(b'XYZ\n'))
            self.stream_reader.readline.expect_call().will_once(Return(b'1.0\n'))
            self.stream_reader.readline.expect_call().will_once(Return(b'12\n'))
            self.stream_reader.read.expect_call(12).will_once(Return(b'Hello world!'))
            assert self.uut.read() == b'Hello world!'

        def test_when_invalid_magic_bytes_received__then_xyz_error_is_raised(self):
            self.stream_reader.readline.expect_call().will_once(Return(b'ABC\n'))
            with pytest.raises(XYZError) as excinfo:
                self.uut.read()
            assert str(excinfo.value) == "Invalid magic bytes: b'ABC'"

        def test_when_invalid_version_received__then_xyz_error_is_raised(self):
            self.stream_reader.readline.expect_call().will_once(Return(b'XYZ\n'))
            self.stream_reader.readline.expect_call().will_once(Return(b'2.0\n'))
            with pytest.raises(XYZError) as excinfo:
                self.uut.read()
            assert str(excinfo.value) == "Unsupported version: b'2.0'"

.. testcode::
    :hide:

    tc = TestXYZReader()
    for name in dir(tc):
        if name.startswith('test_'):
            test = getattr(tc, name)
            tc.setup_method()
            test()
            tc.teardown_method()

.. tip::
    Alternatively you can use **fixtures** instead of **setup_method()** and
    **teardown_method()**. Fixtures are way more powerful. For more details
    please visit https://docs.pytest.org/en/latest/fixture.html.

We've moved mock (1) and unit under test (2) construction into
**setup_method()** method and used :func:`mockify.assert_satisfied` function
(3) in **teardown_method()**. That function works the same as
:func:`mockify.satisfied`, but is not a context manager. Notice that we've
also removed context manager from OK test, as it is no longer needed.

Now, once tests are refactored, you can just add another tests without even
remembering to check the mock before test is done - it all happens
automatically. And the tests look much cleaner than before refactoring. There
is even more: you can easily extract recording expectations to separate
methods if needed.

Putting it all together
-----------------------

Here's once again complete **XYZReader** class:

.. testcode::

    class XYZError(Exception):
        pass

    class XYZReader:

        def __init__(self, stream_reader):
            self._stream_reader = stream_reader

        def read(self):
            magic_bytes = self._stream_reader.readline()
            magic_bytes = magic_bytes.rstrip()
            if magic_bytes != b'XYZ':
                raise XYZError("Invalid magic bytes: {!r}".format(magic_bytes))
            version = self._stream_reader.readline()
            version = version.rstrip()
            if version != b'1.0':
                raise XYZError("Unsupported version: {!r}".format(version))
            payload_size = self._stream_reader.readline()
            payload_size = payload_size.rstrip()
            payload_size = int(payload_size)
            return self._stream_reader.read(payload_size)

And tests:

.. testcode::

    import pytest

    from mockify import assert_satisfied
    from mockify.mock import Mock
    from mockify.actions import Return

    class TestXYZReader:

        def setup_method(self):
            self.stream_reader = Mock('stream_reader')  # (1)
            self.uut = XYZReader(self.stream_reader)  # (2)

        def teardown_method(self):
            assert_satisfied(self.stream_reader)  # (3)

        def test_read_xyz_message(self):
            self.stream_reader.readline.expect_call().will_once(Return(b'XYZ\n'))
            self.stream_reader.readline.expect_call().will_once(Return(b'1.0\n'))
            self.stream_reader.readline.expect_call().will_once(Return(b'12\n'))
            self.stream_reader.read.expect_call(12).will_once(Return(b'Hello world!'))
            assert self.uut.read() == b'Hello world!'

        def test_when_invalid_magic_bytes_received__then_xyz_error_is_raised(self):
            self.stream_reader.readline.expect_call().will_once(Return(b'ABC\n'))
            with pytest.raises(XYZError) as excinfo:
                self.uut.read()
            assert str(excinfo.value) == "Invalid magic bytes: b'ABC'"

        def test_when_invalid_version_received__then_xyz_error_is_raised(self):
            self.stream_reader.readline.expect_call().will_once(Return(b'XYZ\n'))
            self.stream_reader.readline.expect_call().will_once(Return(b'2.0\n'))
            with pytest.raises(XYZError) as excinfo:
                self.uut.read()
            assert str(excinfo.value) == "Unsupported version: b'2.0'"

.. testcode::
    :hide:

    tc = TestXYZReader()
    for name in dir(tc):
        if name.startswith('test_'):
            test = getattr(tc, name)
            tc.setup_method()
            test()
            tc.teardown_method()

And that's the end of quickstart guide :-)

Now you can proceed to :ref:`Tutorial` section, covering some more advanced
features, or just try it out in your projects. Thanks for reaching that far.
I hope you will find Mockify useful.
