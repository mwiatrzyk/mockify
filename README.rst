============
Mockify v0.1
============

I. About
--------

Mockify is a Python mocking library with syntax similar to Google Mock (a.k.a.
GMock) C++ library that I was using during writing code in C++. I started
writing Mockify when I noticed that ``unittest.mock`` from Python standard
library does not have such expressive API that GMock has and for what I liked
it. And since GMock is fun and pretty easy to use, why not try mocking in
similar way in Python?

II. Features
------------

1) Easy to use, expressive syntax::

    >>> from mockify import Context
    >>> ctx = Context()
    >>> foo = ctx.make_mock("foo")
    >>> foo.expect_call(1, 2).times(2)
    <Expectation: mock_call=foo(1, 2), expected='to be called twice', actual='never called'>
    >>> foo.expect_call(3, 4)
    <Expectation: mock_call=foo(3, 4), expected='to be called once', actual='never called'>
    >>> foo(1, 2)
    >>> foo(1, 2)
    >>> foo(3, 4)
    >>> ctx.assert_satisfied()

2) Support for ordered and unordered expectation resolving.

3) Support for side effects and matchers.
