Installation
============

Using *virtualenv* and *pip*
----------------------------

Todo.

Directly from source code using *pip*
-------------------------------------

Todo.

By embedding Mockify source inside your project
-----------------------------------------------

.. note::

    This is not recommended.

    Using this approach Mockify will become part of your source code, therfore
    updating it to newer version would require repeating steps listed below.
    Use this only if for some reason *pip* is not solution for you.

Here is short instruction of how to embed Mockify inside your project.

1) Clone Mockify repository::

    $ git clone https://gitlab.com/z3fir/mockify.git

2) Create a directory inside root directory of your project. Usually, this is
   named ``3rdparty`` or something like this::

    $ mkdir /path/to/your_project/3rdparty

3) Copy Mockify source code (directory ``mockify`` in project's root directory)
   to directory created in previous step::

    $ cp -r /path/to/mockify/mockify /path/to/your_project/3rdparty/

4) Now you have to tell Python where to look for another libraries. And since
   Mockify is only used for testing, you would do this inside
   ``[your_project]/tests/__init__.py`` file (or similar). Edit that file and
   add following code inside::

    import os
    import sys

    this_dir = os.path.abspath(os.path.dirname(__file__))
    root_dir = os.path.join(this_dir, '..')

    sys.path.insert(0, os.path.join(root_dir, '3rdparty'))

   The code above is getting absolute path to your project's root directory and
   then adds absolute path to previously created ``3rdparty`` directory, which
   already has ``mockify`` directory with Mockify source code.

5) Now you should be able to import Mockify module::

    import mockify
