.. Mockify documentation master file, created by
   sphinx-quickstart on Fri Nov  9 08:43:36 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Mockify!
===================

Welcome to Mockify library documentation!

Mockify is a mocking toolkit for Python inspired by Google Mock framework for
C++ language. I started writing it when I noticed that :mod:`unittest.mock`
module from standard library is based on checking if given function was called
with given args, when Google Mock I've been using a lot as a C++ developer
works by recording **expectations** on a mock **before** it is called. And
since I was more often using Google Mock than :mod:`unittest.mock` during last
few years, the more natural way of mocking things was (at least for me) the one
introduced by Google Mock.

And that's how Mockify works :-)

User's Guide
------------

.. toctree::
   :maxdepth: 3

   installation
   tutorial
   examples



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
