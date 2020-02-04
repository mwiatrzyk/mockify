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

.. toctree::
    :maxdepth: 3

    tutorial/using-mock-class
    tutorial/using-mock-factory-class
    tutorial/using-sessions
    tutorial/recording-actions
    tutorial/setting-expected-call-count-range
    tutorial/using-matchers
    tutorial/using-ordered
    tutorial/patching-imports

Creating mocks
--------------

Introduction
^^^^^^^^^^^^

Mockify provides a general purpose :class:`mockify.mock.Mock` class for
creating mocks:

.. testcode::

    from mockify.mock import Mock

This class can be used to mock standalone functions, objects with methods and
properties, modules and to create ad-hoc data objects.

To create mock object, you have to name it and, optionally, give it instance of
:class:`mockify.Session` class. Sessions are generally placeholders for
expectation objects. Each mock can create its own session (by default) or use
a shared one. Some features of Mockify work only on shared sessions. You can
read more about sessions in :ref:`Using sessions` section.

To name a mock you must use a name that is a valid Python identifier, or
valid Python module name. It is recommended to use same name as name of
variable the mock is assigned to:

.. testcode::

    foo = Mock('foo')
    foo_bar = Mock('foo.bar')

And if you give invalid name, an exception will be raised:

.. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> Mock('123')
    Traceback (most recent call last):
        ...
    TypeError: Mock name must be a valid Python identifier, got '123' instead

Mock names are important, because they are used in error reports. If you
choose wrong name for your mock, then test failures might potentially be
misleading.

Let's now see how to use mocks in some practical situations.

Mocking functions
^^^^^^^^^^^^^^^^^

We'll start with mocking Python functions.

Look at this function:

.. testcode::

    def find_first(func, iterable):
        for item in iterable:
            if func(item):
                return item

It uses user defined *func* to find first matching element in given
*iterable*. To test that function with Mockify we need to mock *func*, so
let's create a mock *func* first:

.. testcode::

    func = Mock('func')

Mock objects are callable, so basically that is already our function mock.
But if you try to use it before any expectations are recorded, you'll get
:exc:`mockify.exc.UninterestedCall` error:

.. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> find_first(func, [1, 2, 3])
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: No expectations recorded for mock:
    <BLANKLINE>
    at <doctest default[0]>:3
    -------------------------
    Called:
      func(1)

And to record expectations on a function mocks, just use *expect_call* method
like in this example:

.. testcode::

    from mockify.actions import Return

    func.expect_call(1).will_once(Return(True))

We've recorded that *func* will be called with single positional argument of
value ``1`` and, when called, it will return ``True``. Now our example
function will pass and return first item from the sequence:

.. doctest::

    >>> find_first(func, [1, 2, 3])
    1

Mocking methods
^^^^^^^^^^^^^^^
Let's assume we want to test following class:

.. testcode::

    class StreamReader:

        def __init__(self, stream, chunk_size=4096):
            self._stream = stream
            self._chunk_size = chunk_size

        def read(self, count):
            result = b''
            bytes_left = count
            while bytes_left > 0:
                chunk = self._stream.read(min(self._chunk_size, bytes_left))
                bytes_left -= len(chunk)
                result += chunk
            return result

This class is a sort of decorator pattern implementation (in terms of design
patterns) that adds functionality to read exact amount of bytes from
underlying low-level *stream* object which does not guarantee that. To test
*StreamReader* we need to mock *stream* object and its *read()* method.

First of all, we need to create a mock:

.. testcode::

    stream = Mock('stream')

Now let's use the mock and call *StreamReader.read()* method. We'll receive
:exc:`mockify.exc.UninterestedCall` error:

.. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> reader = StreamReader(stream, chunk_size=2)
    >>> reader.read(3)
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: No expectations recorded for mock:
    <BLANKLINE>
    at <doctest default[0]>:11
    --------------------------
    Called:
      stream.read(2)

As you can see, *StreamReader* tried to call
*stream.read()* method but failed due to lack of expectations. To record
expectations on mock's "methods" you have to prefix *expect_call()*
additionally with method's name, like in example below:

.. testcode::

    stream.read.expect_call(2).will_once(Return(b'AB'))
    stream.read.expect_call(1).will_once(Return(b'C'))

We have two expectations, because we expect *StreamReader* to read single
message with two calls to underlying *stream* object. That's because we've
set maximal chunk size to be less than requested byte count.

And let's try to read once again - it will return ``b'ABC'``, the
concatenation of what we've given in expectations:

.. doctest::

    >>> reader.read(3)
    b'ABC'

Mocking property getters and setters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::
    Since version 1.0.0 of Mockify, recording property getting and setting is
    implemented in form of recording call expectation of *__getattr__* and
    *__setattr__* (accordingly) special methods. That makes it clear,
    consistent with the rest of the library and easy to remember and
    understand.

Mocking getters
~~~~~~~~~~~~~~~

For example, let's record that *foo* property will be get once and it will
return ``'foo value'`` when called:

.. testcode::

    mock = Mock('mock')
    mock.__getattr__.expect_call('foo').will_once(Return("foo value"))

Now if you get *foo*, it will return the value:

.. doctest::

    >>> mock.foo
    'foo value'

But since we've recorded single return value, getting it once again will
result in :exc:`mockify.exc.OversaturatedCall` exception:

.. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> mock.foo
    Traceback (most recent call last):
        ...
    mockify.exc.OversaturatedCall: Following expectation was oversaturated:
    <BLANKLINE>
    at <doctest default[0]>:2
    -------------------------
    Pattern:
      mock.__getattr__('foo')
    Expected:
      to be called once
    Actual:
      oversaturated by mock.__getattr__('foo') at <doctest default[0]>:1 (no more actions)

That is not intuitive, why can't we just retrieve the property again? Well,
in fact we are not getting any properties, but calling a mock behind the
scenes and it has only single action recorded. But we can set persistent
values as well using *will_repeatedly()* function (more about that in
:ref:`Recording actions` secion):

.. testcode::

    mock.__getattr__.expect_call('foo').will_repeatedly(Return('spam'))

And now you can call it any times you want, each time returning same value:

.. doctest::

    >>> mock.foo
    'spam'
    >>> mock.foo
    'spam'

Mocking setters
~~~~~~~~~~~~~~~

To mock a setter, you basically need to do the same, but this time with
*__setattr__* special method. For example, to record that *foo* will be once
set to ``123`` we need following expectation:

.. testcode::

    mock = Mock('mock')
    mock.__setattr__.expect_call('foo', 123)

This time the expectation is a bit different, because *__setattr__* accepts
two arguments (name and value), and returns nothing, so we don't need to
record any actions.

Now you can set *foo* to ``123``:

.. testcode::

    mock.foo = 123

But not to any other value, as there is no matching expectation that would
handle that:

.. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> mock.foo = 456
    Traceback (most recent call last):
        ...
    mockify.exc.UnexpectedCall: No matching expectations found for call:
    <BLANKLINE>
    at <doctest default[0]>:1
    -------------------------
    Called:
      mock.__setattr__('foo', 456)
    Expected (any of):
      mock.__setattr__('foo', 123)

And also, since we've recorded that property will be set **once**, attempt to
set it for the second time will make expectation unsatisfied:

.. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> from mockify import satisfied
    >>> with satisfied(mock):
    ...     mock.foo = 123
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: Following expectation is not satisfied:
    <BLANKLINE>
    at <doctest default[0]>:2
    -------------------------
    Pattern:
      mock.__setattr__('foo', 123)
    Expected:
      to be called once
    Actual:
      called twice

Mocking setters and getters simultaneously
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can record both setting and getting expectations for same property. For
example like that:

.. testcode::

    mock = Mock('mock')
    mock.__setattr__.expect_call('foo', 123)
    mock.__getattr__.expect_call('foo').will_repeatedly(Return(123))

We've just recorded that *foo* will once be set to ``123``, and then it will
have that value set forever. Look:

.. doctest::

    >>> mock.foo = 123
    >>> mock.foo
    123
    >>> mock.foo
    123

Basically, we've emulated read/write property. The test would fail if you set
*foo* to some other value or if you set it more times than expected.

Creating ad-hoc data objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes you may need to return some non-scalar value from your mock.
Consider following example:

.. testcode::

    class API:

        def __init__(self, connection):
            self._connection = connection

        def list_users(self):
            response = self._connection.get('/users')
            if response.code != 200:
                raise Exception('failed to list users')
            return response.json['users']

This class is a facade on top of some *connection* class performing HTTP
queries. To test that class, we need to mock *connection.get()* method, but
that method returns a non-scalar result. We can prepare such *response*
object ad-hoc, using :class:`mockify.mock.Mock` class.

Here's an example:

.. testcode::

    response = Mock('response')
    response.code = 200
    response.json = {'users': ['foo', 'bar']}

    connection = Mock('connection')
    connection.get.expect_call('/users').will_once(Return(response))

    api = API(connection)

And now when you call *list_users()*, it will return what we've just told it
to return:

.. doctest::

    >>> api.list_users()
    ['foo', 'bar']

.. tip::
    If you need such data object in more than one test, then you can make
    some factory or fixture function that will save you some work.

Mocking modules (a.k.a. namespaces)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All features of :class:`mockify.mock.Mock` we've discussed so far can also be
used in form of module paths or namespaces. For example, to expect call of a
method *bar()* of some nested object *foo*, you just record following
expectation:

.. testcode::

    mock = Mock('mock')
    mock.foo.bar.expect_call().will_once(Return(123))

.. doctest::

    >>> mock.foo.bar()
    123

And we can do the same with setters and getters:

.. testcode::

    mock = Mock('mock')
    mock.foo.__setattr__.expect_call('bar', 123)
    mock.foo.__getattr__.expect_call('bar').will_once(Return(123))

.. doctest::

    >>> mock.foo.bar = 123
    >>> mock.foo.bar
    123

And with data objects as well:

.. doctest::

    >>> mock = Mock('mock')
    >>> mock.foo.bar = 123
    >>> mock.foo.spam.more_spam = 'need more spam'
    >>> mock.foo.bar
    123
    >>> mock.foo.spam.more_spam
    'need more spam'

And there is no limit of how deep you can go:

.. testcode::

    mock = Mock('mock')
    mock.it.can.be.very.deep.nested.object.path.expect_call().will_once(Return('indeed'))
    assert mock.it.can.be.very.deep.nested.object.path() == 'indeed'

That makes it pretty easy to mock any nested object calls. This feature of
Mockify is used to implement patching of imported modules. See :ref:`Patching
imports` secion for more details.

Using mock factory
------------------

If you need to create several mocks inside your tests, remembering all of
them may become difficult. To make things easier, Mockify provides
:class:`mockify.mock.MockFactory` class that can create and manage several
mocks at once. Thanks to this, you record expectations on different mocks,
but check all at once using factory object.

Each mock factory ensures that:

* each mock will be created once,
* always same mock object will be returned for given name,
* all created mocks will share one common **session** object (more about
  sessions in :ref:`Using sessions` section).

Here's an example code where you find that useful:

.. testcode::

    import hashlib

    class RegisterUserAction:

        class UserAlreadyRegistered(Exception):
            pass

        def __init__(self, database, mailer):
            self._database = database
            self._mailer = mailer

        def invoke(self, email, password):
            if self._database.user_registered(email):
                raise self.UserAlreadyRegistered()
            password_hash = self._hash_password(password)
            self._database.add_inactive_user(email, password_hash)
            self._mailer.send_activation_email(email)

        def _hash_password(self, password):
            password = password.encode()
            password_hash = hashlib.sha1(password).hexdigest()  # Not safe, but it's an example
            return password_hash

That class implements simplified logic of user registration process. We check
if user is already registered, add it to database and send activation e-mail,
so the user will be able to finalize registration by clicking on the link
that is received.

The *RegisterUserAction* class has two dependencies:

* an interface to database,
* and an interface to some kind of e-mail sending service.

We therefore need two mocks and you would have to remember to check both just
before test ends. And that's were mock factories come into play and help you
deal with that:

.. testcode::

    from mockify.mock import MockFactory

    def test_invoke_register_user_action():
        factory = MockFactory()
        database = factory.mock('database')
        mailer = factory.mock('mailer')

        database.user_registered.\
            expect_call('foo@example.com').will_once(Return(False))
        database.add_inactive_user.\
            expect_call('foo@example.com', 'ce0b2b771f7d468c0141918daea704e0e5ad45db')
        mailer.send_activation_email.\
            expect_call('foo@example.com')

        action = RegisterUserAction(database, mailer)
        with satisfied(factory):
            action.invoke('foo@example.com', 'p@55w0rd')

.. testcleanup::

    test_invoke_register_user_action()

As you can see in the example above, we've created mock factory named
*factory*, then - using it - two mocks: *database* and *mailer*. The rest of
the code is pretty much the same as in all previous examples, but we've used
*factory* instead of two created mocks as argument of *satisfied()* context
manager. Therefore, when factory is used, you only have to remember to check
your factory object - no matter how many mocks were created using it.

Mock factory can also be very handy if you have multiple tests for your unit
under test and need to use test setup and teardown for parts of test code
that are repeating between tests. Here's an example of complete test suite
for *RegisterUserAction* class based on :mod:`unittest` testing toolkit:

.. testcode::

    from unittest import TestCase

    from mockify import assert_satisfied

    class TestRegisterUserAction(TestCase):

        def setUp(self):
            self.factory = MockFactory()
            self.database = self.factory.mock('database')
            self.mailer = self.factory.mock('mailer')
            self.uut = RegisterUserAction(self.database, self.mailer)

        def tearDown(self):
            assert_satisfied(self.factory)

        def test_invoke_register_user_action(self):
            self.database.user_registered.\
                expect_call('foo@example.com').will_once(Return(False))
            self.database.add_inactive_user.\
                expect_call('foo@example.com', 'ce0b2b771f7d468c0141918daea704e0e5ad45db')
            self.mailer.send_activation_email.\
                expect_call('foo@example.com')

            self.uut.invoke('foo@example.com', 'p@55w0rd')

        def test_when_user_name_already_exists__an_exception_is_raised(self):
            self.database.user_registered.\
                expect_call('foo@example.com').will_once(Return(True))

            with self.assertRaises(RegisterUserAction.UserAlreadyRegistered):
                self.uut.invoke('foo@example.com', 'p@55w0rd')

.. testcleanup::

    import contextlib

    @contextlib.contextmanager
    def assert_raises(exc):
        try:
            yield
        except exc:
            pass
        else:
            raise AssertionError(f"EXCEPTION NOT RAISED: {exc}")

    tc = TestRegisterUserAction()
    tc.assertRaises = assert_raises  # Don't know why this does not work...
    tests = [
        tc.test_invoke_register_user_action,
        tc.test_when_user_name_already_exists__an_exception_is_raised]
    for test in tests:
        tc.setUp()
        test()
        tc.tearDown()

In example above we've used *setUp()* method to create factory, all mocks,
and unit under test. Next, all our tests use mocks created during setup
phase. Finally, after each test, :meth:`mockify.assert_satisfied` is used on
factory object to check if all mocks are satisfied. Following that approach
we can have automated base part of our test, and create mocks when needed
using factory object.

.. tip::
    If you are using :mod:`pytest` framework for testing (which I personally
    highly recommend), things can become even easier with a use of
    **fixtures**:

    .. testcode::

        import pytest

        from mockify import satisfied
        from mockify.mock import MockFactory

        @pytest.fixture
        def mock_factory():
            factory = MockFactory()
            with satisfied(factory):
                yield factory

        def test_something(mock_factory):
            mock = mock_factory.mock('mock')
            # ....

Using sessions
--------------

What is a session?
^^^^^^^^^^^^^^^^^^

A core part of Mockify library is a **session**. Sessions are automatically
created for each mock or mock factory, but can also be created explicitly
using :class:`mockify.Session` class and passed to mocks/mock factories via
*session* parameter. Sessions can be shared between multiple mocks or mock
factories, and some features of Mockify (like ordered expectations, see
:ref:`Ordered expectations` for more details) will require common session to
be used.

Each session instance receive mock calls and expectation registrations from
all mocks that use that session. A session may therefore be perceived as a
kind of **expectation resolver**, because in fact all happens inside a
session - mocks or mock factories are only facades on top of it.

Sessions can be used in similar way as mock factories - you can create one
inside setup part of the test, and verify later in teardown. Then, after
session is created, you can use it for example to create mock factory. Here's
an example in :mod:`pytest`:

.. testcode::

    import pytest

    from mockify import Session
    from mockify.mock import MockFactory

    @pytest.fixture
    def mock_session():
        session = Session()
        yield session
        session.done()

    @pytest.fixture
    def mock_factory(mock_session):
        factory = MockFactory(session=mock_session)
        return factory

    def test_something(mock_factory):
        mock = mock_factory.mock('mock')
        # ....

Although this may be seen as too complicated (since mock factory is good
enough to provide same functionality), but you will have to create session
manually to change some of Mockify internal behavior for mocks that share
that session.

And now let's have a brief tour on what can be changed.

Changing uninterested call strategy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, when you call a mock that does not have any expectations
recorded, the call will fail with uninterested call error. But this default
behavior can be changed by setting ``'uninterested_call_strategy'`` config
option. Following values for that option are available:

``'fail'``
    This is the default.

    When there are no expectations found for mock call,
    :exc:`mockify.exc.UninterestedCall` exception is raised.

``'ignore'``
    Any calls that have no matching expectations found are silently ignored
    and test is not terminated instantly.

``'warn'``
    Same as ``'ignore'``, but :exc:`mockify.exc.UninterestedCallWarning`
    warning is emitted.

To change session options you have to use :meth:`mockify.Session.configure`
method. Here's an example of setting ``'ignore'`` uninterested call strategy:

.. testcode::

    from mockify import Session
    from mockify.mock import Mock

    session = Session()
    session.configure('uninterested_call_strategy', 'ignore')

    first = Mock('first', session=session)
    first.foo()  # This will not fail...

    second = Mock('second', session=session)
    second.bar()  # ...and this either

If you run that code, both *first* and *second* mocks won't fail, as we've
changed uninterested call strategy for them.

Recording actions
-----------------

Introduction
^^^^^^^^^^^^

Let's create a mock and record most basic expectation on it:

.. testcode::

    mock = Mock('mock')
    mock.expect_call()

If now that mock is called, it will return ``None``:

.. doctest::

    >>> mock() is None
    True

This is the default behavior, and you would use it to mock methods or
functions that have no side effects. But what if mocked method needs to
return a value or raise an exception? For that purpose Mockify provides
**actions** that are available under :mod:`mockify.actions` module.

Setting return value
^^^^^^^^^^^^^^^^^^^^

To set return value on a mock, use :class:`mockify.actions.Return` action:

.. testcode::

    from mockify.actions import Return

    mock = Mock('mock')
    mock.expect_call().will_once(Return('It works!'))

If you now call that mock, it will return what we've just told it to return:

.. doctest::

    >>> mock()
    'It works!'

Setting exception to be raised
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want your mock to raise given exception when called, use
:class:`mockify.actions.Raise` action:

.. testcode::

    from mockify.actions import Raise

    mock = Mock('mock')
    mock.expect_call().will_once(Raise(TypeError('got error')))

If now mock is called, it will raise :exc:`TypeError` we've told it to raise:

.. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> mock()
    Traceback (most recent call last):
        ...
    TypeError: got error

Setting custom function to be invoked by mock
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If needed, you can set a custom function to be executed when mock is called.
Such function will receive all arguments mock was called with, and value it
returns (or exception it raises) will also be used by mock:

.. testcode::

    from mockify.actions import Invoke

    def func(a, b, c):
        return (a, b, c)

    mock = Mock('mock')
    mock.expect_call(1, 2, c=3).will_once(Invoke(func))

Now, when mock is called, it will pass all its arguments to given *func*, and
that function will return given arguments packed into tuple:

.. doctest::

    >>> mock(1, 2, c=3)
    (1, 2, 3)

You can also bind arguments to function:

.. testcode::

    mock.expect_call('middle').will_once(Invoke(func, 'first', c='last'))

.. doctest::

    >>> mock('middle')
    ('first', 'middle', 'last')

This is the most generic action.

Recording action chains
^^^^^^^^^^^^^^^^^^^^^^^

So far we've recorded only one action, implicitly expecting mock to be
executed once. But it is possible to record more actions simply by making
chained call to *will_once()* method, giving it next action to be executed
and increasing expected mock call count each time by one.

For example, let's now record 3 return values:

.. testcode::

    mock = Mock('mock')
    mock.expect_call().\
        will_once(Return(1)).\
        will_once(Return(2)).\
        will_once(Return(3))

Now each time *mock()* is called, next available action is executed:

.. doctest::

    >>> mock()
    1
    >>> mock()
    2
    >>> mock()
    3

And now the mock is satisfied - it was called three times and all actions
were consumed:

.. testcode::

    assert_satisfied(mock)

Recording repeated actions
^^^^^^^^^^^^^^^^^^^^^^^^^^

In Mockify there also are so called **repeated actions**. Repeated actions
are useful if you need to make your mock, for example, returning always the
same value. When repeated action is recorded on given expectation, it can be
executed any number of times (including zero), unless explicitly limited (see
:ref:`Setting expected call count` for details). To record repeated action,
you will have to call **will_repeatedly()** method on expectation object and
give it an action:

.. testcode::

    mock = Mock('mock')
    mock.expect_call().will_repeatedly(Return('repeated'))

With repeated action declared in that way, a mock is already satisfied:

.. testcode::

    assert_satisfied(mock)

And if you call it several times, it will always return same value:

.. doctest::

    >>> mock()
    'repeated'
    >>> mock()
    'repeated'

Setting expected call count
---------------------------

In Mockify you will not find any method for checking if mock was called given
number of times. Instead, you can set expected call count on expectations
using :meth:`mockify.Expectation.times` method.

Expecting mock to be never called
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to record expectation that mock will never be called. Here's
an example:

.. testcode::

    mock = Mock('mock')
    mock.foo.expect_call(0).times(0)

Here we have recorded that *mock.foo(0)* is expected to be **never** called.
If you now invoke that mocked method, you'll see that nothing happens:

.. testcode::

    mock.foo(0)

But if you now check if mock is satisfied, :exc:`mockify.exc.Unsatisfied`
error will be reported:

.. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> assert_satisfied(mock)
    Traceback (most recent call last):
        ...
    mockify.exc.Unsatisfied: Following expectation is not satisfied:
    <BLANKLINE>
    at <doctest default[0]>:2
    -------------------------
    Pattern:
      mock.foo(0)
    Expected:
      to be never called
    Actual:
      called once

That can be useful to explicitly state that mock is not allowed to be called
with given set of params, and to avoid :exc:`mockify.exc.UninterestedCall`
exception that would be raised during mock call if we didn't record any
expectation.

Expecting mock to be called given number of times
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you record expectation without use of *times()* method, then you
**implicitly** expect your mock to be called once. But there are some
scenarios you will need to set higher count of expected calls. For example,
if mock gets called in a loop:

.. testcode::

    import time

    class RetryProxy:

        def __init__(self, connection, retry_count=3, retry_interval=100):
            self._connection = connection
            self._retry_count = retry_count
            self._retry_interval = retry_interval

        def get(self, url):
            count = self._retry_count
            while count > 0:
                response = self._connection.get(url)
                if response is not None:
                    return response
                time.sleep(self._retry_interval)
                count -= 1

Using matchers
--------------

Patching imports
----------------

Customizing Mockify
-------------------

Creating custom actions
^^^^^^^^^^^^^^^^^^^^^^^
