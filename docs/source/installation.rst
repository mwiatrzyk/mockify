.. ----------------------------------------------------------------------------
.. docs/source/installation.rst
..
.. Copyright (C) 2018 - 2019 Maciej Wiatrzyk
..
.. This file is part of Mockify library documentation
.. and is released under the terms of the MIT license:
.. http://opensource.org/licenses/mit-license.php.
..
.. See LICENSE.txt for details.
.. ----------------------------------------------------------------------------
Installation
============

From PyPI using *virtualenv* and *pip*
--------------------------------------

Mockify can be installed by simply invoking this inside active virtual Python
environment::

    $ pip install mockify

This will install most recently deployed version of the library.

You can also add Mockify to your *requirements.txt* file if your project
already has one. After that, you can install all dependencies at once using
this command::

    $ pip install -r requirements.txt

Directly from source using *virtualenv* and *pip*
-------------------------------------------------

You can also install Mockify directly from source code by simply invoking this
command inside active virtual Python environment::

    $ pip install git+https://gitlab.com/zef1r/mockify.git@[branch-or-tag]

This will allow you to install most recent version of the library that may not
be released yet to PyPI. And also you will be able to install from any branch
and tag.

Verifying installation
----------------------

Once Mockify is installed, you can simply check if it works by invoking this
code to print version of installed Mockify library::

    import mockify

    print(mockify.version)

And you're now ready to use Mockify for mocking things in your tests. Please
proceed to :ref:`Tutorial` section of this documentation to learn how to use
it.
