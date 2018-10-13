Mockify
=======

Mocking library for Python.

About
-----

The purpose of using Mockify is the same as for Python's standard
:mod:`unittest.mock` mocking library - to mimic behaviour of things during
testing. But Mockify uses a different approach to achieve that goal.

Mockify does not have multiple ``assert_called_*`` methods that are executed to
check if a method was called. Instead, it uses ``expect_call`` method to record
expectations on a mock function.  

These expectations are recorded on common (for selected mock functions) context
object, that acts as a registry and call tracker.

Documentation
-------------

Newest documentation can be found at https://mockify.readthedocs.org/.

License
-------

This software is released under the terms of the MIT license.

See **LICENSE.txt** for details.
