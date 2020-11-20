![PyPI - License](https://img.shields.io/pypi/l/mockify)
![PyPI](https://img.shields.io/pypi/v/mockify)
![PyPI - Downloads](https://img.shields.io/pypi/dm/mockify)
[![codecov](https://codecov.io/gl/zef1r/mockify/branch/master/graph/badge.svg?token=UX2T69XQAJ)](https://codecov.io/gl/zef1r/mockify)

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
from mockify.core import satisfied
from mockify.mock import Mock
from mockify.actions import Return

def func_caller(func):
    return func()

def test_func_caller():
    func_mock = Mock('greet')
    func_mock.expect_call().will_once(Return('Hello, world!'))
    with satisfied(func_mock):
        assert func_caller(func_mock) == 'Hello, world!'
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
