Mockify
=======

Mocking library for Python inspired by Google Mock C++ mocking toolkit.

About
-----

The purpose of using Mockify is the same as for Python's ``unittest.mock``
module - to mimic behaviour of things during testing. But Mockify uses a
different approach to do that.

Mockify does not have multiple ``assert_called_*`` methods that are executed to
check if a method was called. Instead, it uses ``expect_call`` method to record
expectations on mocks *before* they are called, and after unit under test is
executed, mocks are checked if all recorded expectations are satisfied using
one ``assert_satisfied`` assertion method.

Documentation
-------------

Newest documentation can be found at https://mockify.readthedocs.org/.

Source
------

Source code is available at https://gitlab.com/zef1r/mockify/.

License
-------

This software is released under the terms of the MIT license.

See **LICENSE.txt** for details.
