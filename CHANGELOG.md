(unreleased)
------------

**Added**

  * New action added: :class:`mockify.actions.YieldAsync`
  * New action added: :class:`mockify.actions.ReturnContext`

0.11.0 (2020-11-24)
-------------------

**Added**

  * New action added: :class:`mockify.actions.ReturnAsync`
  * New action added: :class:`mockify.actions.IterateAsync`
  * New action added: :class:`mockify.actions.RaiseAsync`
  * New action added: :class:`mockify.actions.InvokeAsync`

**Changed**

  * Abstract method :meth:`mockify.actions.Action.format_params` was removed
    and :meth:`mockify.actions.Action.__str__` is now made abstract instead

  * Abstract method :meth:`mockify.cardinality.ExpectedCallCount.format_params`
    was removed and :meth:`mockify.cardinality.ExpectedCallCount.__repr__` is
    now made abstract instead

**Deprecated**

  * Methods :meth:`mockify.core.BaseMock.__m_fullname__` and
    :meth:`mockify.core.BaseMock.__m_walk__` are made deprecated and will be
    removed in one of upcoming releases; functionality is now provided
    completely by class :class:`mockify.core.MockInfo` (which was previously
    acting as a proxy)

**Other**

  * Added CLI tasks to serve documentation and coverage locally for development
    purposes

0.10.0 (2020-11-13)
-------------------

**Added**

  * Added support for Python 3.9

**Other**

  * Using ``tox`` to run tests against supported Python versions
  * Improved packaging according to https://github.com/pypa/sampleproject
    example project

0.9.1 (2020-11-09)
------------------

**Other**

  * Added job to publish coverage reports to https://codecov.io/gl/zef1r/mockify
  * Using ``-pe`` as default mode to ``invoke`` task runner (with help of
    config file)
  * Since now, tags are verified by CI **before** publishing to any PyPI, so it
    will not be possible to publish to test PyPI and to not publish to production
    PyPI (or vice-versa)

0.9.0 (2020-11-08)
------------------

**Added**

  * Added :mod:`mockify.core` module to replace importing of core stuff directly
    from ``mockify`` root module.

    So instead of doing this::

      from mockify import satisfied

    It is recommended to do this::

      from mockify.core import satisfied

    This was changed because importing things directly from root module is
    discouraged, as it leads to longer import times.

**Deprecated**

  * Importing core parts of library directly from ``mockify`` core module is now
    deprecated - use :mod:`mockify.core` instead.

    Since one of upcoming non-fix releases importing core parts of library
    from ``mockify`` core module will not work, unless you will use this::

      from mockify import core

**Fixed**

  * Fixed some ``pylint`` bugs

**Other**

  * Changelog was reformatted and split into sections in accordance to
    https://keepachangelog.com/en/1.0.0/
  * Added tools for code formatting
  * Added ``pylint`` linter
  * Small refactoring of project's development tools

0.8.1 (2020-08-17)
------------------

**Fixed**

  * Small fix in :class:`mockify.matchers.Object` class to make it work when
    :class:`mockify.matchers.Any` matcher is used as its argument and always
    inequal object is used when comparing

0.8.0 (2020-08-08)
------------------

**Added**

  * Added :class:`mockify.core.BaseMock` that acts as common abstract base class
    for all mocks.

    Already existing classes :class:`mockify.mock.Mock` and
    :class:`mockify.mock.MockFactory` now inherit from it.
  * Added :class:`mockify.mock.FunctionMock` for mocking Python functions and to
    be used internally when implementing complex mock classes
  * Added :class:`mockify.mock.ABCMock` for implementing interfaces defined with
    help of :mod:`abc` module

0.7.1 (2020-06-17)
------------------

**Fixed**

  * Fix :class:`mockify.matchers.Object` matcher to be inequal to reference
    object if reference object does not have one or more properties listed in
    matcher

0.7.0 (2020-06-17)
------------------

**Fixed**

  * An alias to 0.6.5 to fix versioning (new feature was introduced, and wrong
    version part was increased by mistake)

0.6.5 (2020-05-15)
------------------

**Added**

  * Added :class:`mockify.matchers.Object` matcher

0.6.4 (2020-02-26)
------------------

**Added**

  * New actions introduced (see :mod:`mockify.actions`)
  * New matchers introduced (see :mod:`mockify.matchers`)
  * New assertion errors introduced and improved exception hierarchy (see
    :mod:`mockify.exc`)
  * Can now define ordered expectations with :func:`mockify.core.ordered` context manager
  * Can now patch imports using :func:`mockify.core.patched` context manager

**Changed**

  * Deprecated code was removed
  * Class **Registry** was renamed to :class:`mockify.core.Session`
  * All classes for making mocks were replaced by single generic
    :class:`mockify.mock.Mock` class, supported by
    :class:`mockify.mock.MockFactory` class

**Fixed**

  * Better reporting of expectation location in assertion messages

**Other**

  * Improved documentation
  * Documentation is now tested by Sphinx
  * CI workflow updated + added testing against various Python versions (3.x for
    now)
  * Many other improvements in the code and the tests

0.5.0 (2019-07-27)
------------------

**Added**

  * Added :class:`mockify.mock.Namespace` mock class

**Changed**

  * Class :class:`mockify.mock.Object` can now be used without subclassing and
    has API similar to other mock classes
  * Module *mockify.helpers* was merged to library core
  * Module *mockify.times* was renamed to :mod:`mockify.cardinality`
  * Module *mockify.engine* is now available via :mod:`mockify`
  * Modules *mockify.mock.function* and *mockify.mock.object* are now merged into
    :mod:`mockify.mock`

**Other**

  * Dependency management provided by **pipenv**
  * Project's CLI provided by Invoke library
  * Use Sphinx Read The Docs theme for documentation

0.4.0 (2019-07-24)
------------------

**Added**

  * Added strategies for dealing with unexpected calls

0.3.1 (2019-01-16)
------------------

**Added**

  * Added frontend for mocking Python objects

0.2.1 (2019-01-05)
------------------

**Added**

  * Added *FunctionFactory* mocking utility

**Changed**

  * Changed Registry.assert_satisfied method to allow it to get mock names to
    check using positional args

**Other**

  * Updated copyright notice
  * Added description to Alabaster Sphinx theme used for docs
  * Script for running tests added (pytest wrapper)
  * Updated copyright.py script and hardcode year the project was started and
    author's name

0.1.12 (2019-01-01)
-------------------

* First release published to PyPI
