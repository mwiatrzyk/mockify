.. Mockify documentation master file, created by
   sphinx-quickstart on Fri Nov  9 08:43:36 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Mockify!
===================

Welcome to Mockify library documentation!

Mockify is a mocking toolkit for Python inspired by GMock (Google Mock) C++
framework. I was using GMock a lot during my 5 years of work as a C++ developer
and really liked it for its expressive API. During that days I was still
writing some Python code (mostly in Python 2.x) and for testing it I was using
hand-written stubs when needed. When I used :mod:`unittest.mock` for the first
time I noticed that it uses a very different approach than GMock I got used to,
so I decided to start writing my own toolkit.

Currently, Mockify is supplied with following features:

    * Creating mocks of standalone functions (more will come soon...)
    * Recording call expectations with fixed arguments and using **matchers**
    * Checking if expectations are satisfied using one single
      ``assert_satisfied`` assertion method
    * Configuring recorded expectations:
        - setting expected call count
        - recording single and repeated actions (a.k.a. side effects)
        - chaining actions

I hope you will find this library useful :-)

User's Guide
------------

.. toctree::
   :maxdepth: 3

   installation
   tutorial
   examples
