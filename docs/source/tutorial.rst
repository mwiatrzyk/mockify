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

.. .. doctest::
    :options: -IGNORE_EXCEPTION_DETAIL

    >>> partial()
    Traceback (most recent call last):
        ...
    mockify.exc.UninterestedCall: No expectations recorded for mock:
    <BLANKLINE>
    at <doctest default[0]>:11
    --------------------------
    Called:
      func()
    Expected:
      no expectations recorded

.. toctree::
    :maxdepth: 1

    tutorial/introduction
    tutorial/creating-mocks
    tutorial/setting-expected-call-count
