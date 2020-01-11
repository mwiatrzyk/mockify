Mockify
=======

Highly customizable and expressive mocking library for Python.

About
-----

Mockify is a library inspired by Google Mock C++ framework, but adopted to
Python world.

Mockify is based on **expectations** that you need to record on your mocks
**before** those are called by code you're testing. And expectations you're
recording are basically assertions that must pass before test ends. Along
with expectations you can also record actions the mock will execute once
called. And all of these is provided by simple, expressive and easy to use
API.

Here's a simple example:

```python
from mockify import satisfied
from mockify.mock import Mock
from mockify.actions import Return

greet = Mock('greet')
greet.expect_call().will_once(Return('Hello, world!'))

with satisfied(greet):
  assert greet() == 'Hello, world!'
```

Mockify allows you to:

* Record expectations with any number of positional and/or keyword arguments,
* Set expected call count or call count range,
* Record **action chains**, allowing subsequent action can be performed on
  subsequent call to same mock,
* Record **repeated** actions that can be executed any number of times,
* Use **matchers**, allowing to match range of parameters the mock is called
  with instead of exact ones,
* and more.

I hope you'll find this library useful.

Documentation
-------------

Newest documentation can be found at https://mockify.readthedocs.org/.

Source
------

Source code is available at https://gitlab.com/zef1r/mockify/.

License
-------

This software is released under the terms of the MIT license.
