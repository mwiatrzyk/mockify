.. ----------------------------------------------------------------------------
.. docs/source/tutorial/managing-multiple-mocks.rst
..
.. Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
..
.. This file is part of Mockify library documentation
.. and is released under the terms of the MIT license:
.. http://opensource.org/licenses/mit-license.php.
..
.. See LICENSE for details.
.. ----------------------------------------------------------------------------
.. _managing-multiple-mocks:

Managing multiple mocks
=======================

Introduction
------------

So far we've discussed situations where single mock object is suitable and
fits well. But those are very rare situations, as usually you will need more
than just one mock. Let's now take a look at following Python code:

.. testcode::

    import hashlib
    import base64


    class AlreadyRegistered(Exception):
        pass


    class RegisterUserAction:

        def __init__(self, database, crypto, mailer):
            self._database = database
            self._crypto = crypto
            self._mailer = mailer

        def invoke(self, email, password):
            session = self._database.session()
            if session.users.exists(email):
                raise AlreadyRegistered("E-mail {!r} is already registered".format(email))
            password = self._crypto.hash_password(password)
            session.users.add(email, password)
            self._mailer.send_confirm_registration_to(email)
            session.commit()


That classes implements business logic of user registration process:

* User begins registration by entering his/her e-mail and password,
* System verifies whether given e-mail is already registered,
* System adds new user to users database and marks as "confirmation in progress",
* System sends confirmation email to the User with confirmation link.

That use case has dependencies to database, e-mail sending service and
service that provides some sophisticated way of generating random numbers
suitable for cryptographic use. Now let's write one test for that class:

.. testcode::

    from mockify import satisfied
    from mockify.mock import Mock
    from mockify.actions import Return

    def test_register_user_action():
        session = Mock('session')  # (1)
        database = Mock('database')
        crypto = Mock('crypto')
        mailer = Mock('mailer')

        database.session.\
            expect_call().will_once(Return(session))
        session.users.exists.\
            expect_call('foo@bar.com').will_once(Return(False))
        crypto.hash_password.\
            expect_call('p@55w0rd').will_once(Return('***'))
        session.users.add.\
            expect_call('foo@bar.com', '***')
        mailer.send_confirm_registration_to.\
            expect_call('foo@bar.com')
        session.commit.\
            expect_call()

        action = RegisterUserAction(database, crypto, mailer)

        with satisfied(database, session, crypto, mailer):  # (2)
            action.invoke('foo@bar.com', 'p@55w0rd')

.. testcode::
    :hide:

    test_register_user_action()

We had to create 3 mocks + one additional at (1) for mocking database
session. And since we have 4 mock objects, we also need to remember to verify
them all at (2). And remembering things may lead to bugs in the test code.
But Mockify is supplied with tools that will help you deal with that.

Using mock factories
--------------------

First solution is to use :class:`mockify.mock.MockFactory` class. With that
class you will be able to create mocks without need to use
:class:`mockify.mock.Mock` directly. Morever, mock factories will not allow
you to duplicate mock names and will automatically track all created mocks
for you. Besides, all mocks created by one factory will share same
**session** object and that is important for some of Mockify's features.

Here's our previous test rewritten to use mock factory instead of several
mock objects:

.. testcode::

    from mockify import satisfied
    from mockify.mock import MockFactory
    from mockify.actions import Return

    def test_register_user_action():
        factory = MockFactory()  # (1)
        session = factory.mock('session')
        database = factory.mock('database')
        crypto = factory.mock('crypto')
        mailer = factory.mock('mailer')

        database.session.\
            expect_call().will_once(Return(session))
        session.users.exists.\
            expect_call('foo@bar.com').will_once(Return(False))
        crypto.hash_password.\
            expect_call('p@55w0rd').will_once(Return('***'))
        session.users.add.\
            expect_call('foo@bar.com', '***')
        mailer.send_confirm_registration_to.\
            expect_call('foo@bar.com')
        session.commit.\
            expect_call()

        action = RegisterUserAction(database, crypto, mailer)

        with satisfied(factory):  # (2)
            action.invoke('foo@bar.com', 'p@55w0rd')

.. testcode::
    :hide:

    test_register_user_action()

Although the code did not change a lot in comparison to previous version,
we've introduced a major improvement. At (1) we've created a **mock factory**
instance, which is used to create all needed mocks. Also notice, that right
now we only check factory object at (2), so we don't have to remember all the
mocks we've created. That saves a lot of problems later, when test is
modified; each new mock will most likely be created using *factory* object
and it will automatically check that new mock.

Using mock factories with test suites
-------------------------------------

Mock factories work the best with test suites containing **setup** and
**teardown** customizable steps executed before and after every single test.
Here's once again our test, but this time in form of test suite (written as
an example, without use of any specific framework):

.. testcode::

    from mockify import assert_satisfied
    from mockify.mock import MockFactory
    from mockify.actions import Return

    class TestRegisterUserAction:

        def setup(self):
            self.factory = MockFactory()  # (1)

            self.session = self.factory.mock('session')   # (2)
            self.database = self.factory.mock('database')
            self.crypto = self.factory.mock('crypto')
            self.mailer = self.factory.mock('mailer')

            self.database.session.\
                expect_call().will_repeatedly(Return(self.session))  # (3)

            self.uut = RegisterUserAction(self.database, self.crypto, self.mailer)  # (4)

        def teardown(self):
            assert_satisfied(self.factory)  # (5)

        def test_register_user_action(self):
            self.session.users.exists.\
                expect_call('foo@bar.com').will_once(Return(False))
            self.crypto.hash_password.\
                expect_call('p@55w0rd').will_once(Return('***'))
            self.session.users.add.\
                expect_call('foo@bar.com', '***')
            self.mailer.send_confirm_registration_to.\
                expect_call('foo@bar.com')
            self.session.commit.\
                expect_call()

            self.uut.invoke('foo@bar.com', 'p@55w0rd')

.. testcode::
    :hide:

    tc = TestRegisterUserAction()
    tc.setup()
    tc.test_register_user_action()
    tc.teardown()

Notice, that we've moved factory to ``setup()`` method (1), and created all
mocks inside it (2) along with unit under test instance (4). Also notice that
obtaining database session (3) was also moved to setup step and made optional
with ``will_repeatedly()``. Finally, our factory (and every single mock
created by it) is verified at (5), during teardown phase of test execution.
Thanks to that we have only use case specific expectations in test method,
and a common setup code, so it is now much easier to add more tests to that
class.

.. note::
    If you are using **pytest**, you can take advantage of **fixtures** and
    use those instead of setup/teardown methods::

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
            # ...

.. _using-sessions:

Using sessions
--------------

A core part of Mockify library is a **session**. Sessions are instances of
:class:`mockify.Session` class and their role is to provide mechanism for
storing recorded expectations, and matching them with calls being made.
Normally sessions are created automatically by each mock or mock factory, but
you can also give it explicitly via *session* argument:

.. testcode::

    from mockify import Session
    from mockify.mock import Mock, MockFactory

    session = Session()  # (1)

    first = Mock('first', session=session)  # (2)
    second = MockFactory(session=session)  # (3)

In example above, we've explicity created session object (1) and gave it to
mock *first* (2) and mock factory *second* (3), which now share the session.
This means that all expectations registered for mock *first* or any of mocks
created by factory *second* will be passed to a common session object. Some
of Mockify features, like **ordered expectations** (see
:ref:`recording-ordered-expectations`) will require that to work. Although
you don't have to create one common session for all your mocks, creating
it explicitly may be needed if you want to:

* override some of Mockify's default behaviors (see
  :attr:`mockify.Session.config` for more info),
* write a common part for your tests.

For the sake of this example let's stick to the last point. And now, let's
write a base class for our test suite defined before:

.. testcode::

    from mockify import Session

    class TestCase:

        def setup(self):
            self.mock_session = Session()  # (1)

        def teardown(self):
            self.mock_session.assert_satisfied()  # (2)

As you can see, nothing really interesting is happening here. We are creating
session (1) in **setup** section and checking it it is satisfied (2) in
**teardown** section. And here comes our test from previous example:

.. testcode::

    class TestRegisterUserAction(TestCase):

        def setup(self):
            super().setup()

            self.factory = MockFactory(session=self.mock_session)  # (1)

            self.session = self.factory.mock('session')
            self.database = self.factory.mock('database')
            self.crypto = self.factory.mock('crypto')
            self.mailer = self.factory.mock('mailer')

            self.database.session.\
                expect_call().will_repeatedly(Return(self.session))

            self.uut = RegisterUserAction(self.database, self.crypto, self.mailer)

        def test_register_user_action(self):
            self.session.users.exists.\
                expect_call('foo@bar.com').will_once(Return(False))
            self.crypto.hash_password.\
                expect_call('p@55w0rd').will_once(Return('***'))
            self.session.users.add.\
                expect_call('foo@bar.com', '***')
            self.mailer.send_confirm_registration_to.\
                expect_call('foo@bar.com')
            self.session.commit.\
                expect_call()

            self.uut.invoke('foo@bar.com', 'p@55w0rd')

.. testcode::
    :hide:

    tc = TestRegisterUserAction()
    tc.setup()
    tc.test_register_user_action()
    tc.teardown()

As you can see, ``teardown()`` method was completely removed because it was
no longer needed - all mocks are checked by one single call to
:meth:`mockify.Session.assert_satisfied` method in base class. The part that
changed is a ``setup()`` function that triggers base class setup method, and
a mock factory (1) that is given a session. With this approach you only
implement mock checking once - in a base class for your tests. The only thing
you have to remember is to give a session instance to either factory, or each
of your mocks for that to work.
