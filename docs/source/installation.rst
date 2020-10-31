.. ----------------------------------------------------------------------------
.. docs/source/installation.rst
..
.. Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
..
.. This file is part of Mockify library documentation
.. and is released under the terms of the MIT license:
.. http://opensource.org/licenses/mit-license.php.
..
.. See LICENSE for details.
.. ----------------------------------------------------------------------------

Installation
============

From PyPI using **pipenv**
--------------------------

If your project's dependencies are managed by **pipenv**, simply proceed to
your project's directory and invoke following command::

    $ pipenv install --dev mockify

That will install most recent version of the library and automatically add it
into your project's development dependencies.

From PyPI using **virtualenv** and **pip**
------------------------------------------

If you are using **virtualenv** in your project, just activate it and invoke
following command::

    $ pip install mockify

That will install most recent version of the library.

You can also add Mockify to your **requirements.txt** file if your project
already has one. After that, you can install all dependencies at once using
this command::

    $ pip install -r requirements.txt

Directly from source using **virtualenv** and **pip**
-----------------------------------------------------

You can also install Mockify directly from source code by simply invoking this
command inside active virtual Python environment::

    $ pip install git+https://gitlab.com/zef1r/mockify.git@[branch-or-tag]

This will allow you to install most recent version of the library that may
not be released to PyPI yet. And also you will be able to install from any
branch or tag.

Verifying installation
----------------------

After installation you can print installed version of Mockify library using
following command::

    $ python -c "import mockify; print(mockify.__version__)"

That command will print version of installed Mockify library. If installation
was not successful, the command will fail.

Now you should be able to start using Mockify.
