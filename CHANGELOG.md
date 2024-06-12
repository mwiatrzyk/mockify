## 0.14.0 (2024-06-12)

### BREAKING CHANGES

- Drop support for Python 3.6 and 3.7

### Feat

- add support for Python 3.10, 3.11 and 3.12

## 0.13.1 (2021-09-20)

### Fix

- ABCMock with no expectations set fails on assert_satisfied

## 0.13.0 (2021-09-10)

### Fix

- fix some of the lint errors in ObjectMock by extracting decorator
- fix mockify.api module
- fixing before release
- fix versioning in setup.py
- fix some of the linter errors

### Feat

- add docstrings explaining interface classes
- add more magic methods that are ready for mocking to ObjectMock class
- add unary __pos__ and __neg__ operators to ObjectMock class
- add __abs__ method to ObjectMock
- add __invert__ method to ObjectMock class
- add __round__, __floor__, __ceil__ and __trunc__ magic methods to ObjectMock
- add more magic method to ObjectMock
- add magic methods to ObjectMock
- add d and tb names to pylint's "good-names" setting
- add BaseFunctionMock and use it as a base for FunctionMock
- add more magic methods to ObjectMock
- add possibilty to mock expect_call method of ObjectMock
- add __all__ property to private submodules

## 0.12.0 (2020-11-29)

### Fix

- fix test failure on py36 by replacing non-existing asynccontextmanager with explicitly created proxy class

### Feat

- add YieldAsync action
- add ReturnContext action
- add ReturnAsyncContext action

## 0.11.0 (2020-11-24)

### Fix

- fix failing test on Py36
- fix tag.py script to update (unreleased) also in docstrings
- fix failing py36 and py37 tests
- fix scripts/tag.py

### Feat

- add ReturnAsync action
- add IterateAsync action
- add changelog entry
- add InvokeAsync action

## 0.10.0 (2020-11-13)

### Fix

- fix in .gitlab-ci.yml

### Feat

- add tox with some basic configuration
- add MANIFEST.in and add tox-based tests to pipeline
- add setup.cfg and pyproject.toml files for better packaging compatibility
- add more metadata info to setup.py
- add documentation link to setup.py
- add support for Python 3.9

## 0.9.1 (2020-11-09)

### Feat

- add invoke.yml config file
- add coverage publish & tag validation jobs
- add codecov.io badge to readme

## 0.9.0 (2020-11-08)

### Fix

- fix mock parent/child hierarchy processing
- fix linter errors
- more pylint errors fixed
- add yapf and reformat code with it
- adjust code with yapf, isort and other tools
- fix more pylint errors in code
- fix coverage task
- fixing linter errors
- fix invoke tasks in pipeline file
- fix .gitlab-ci.yml
- fix docs config
- fix references after creating mockify.core module
- fix in changelog and __init__.py
- fix typo

### Feat

- add gitchangelog to automatically update project's changelog
- add mockify.core documentation
- add some PyPI badges
- add script for updating tag info in __init__.py and CHANGELOG.md

## 0.8.1 (2020-08-17)

### Fix

- fix in Object matcher

## 0.8.0 (2020-08-08)

### Feat

- add ABCMock for automatic mocking of abc.ABC-based interfaces
- add FunctionMock class as a mechanism for easier building of more complex mocks

## 0.7.1 (2020-06-17)

### Fix

- Fix object matcher

## 0.7.0 (2020-06-17)

### Fix

- fix fallback version

## 0.6.5 (2020-05-15)

### Feat

- add Object matcher

## 0.6.4 (2020-02-26)

### Fix

- fix failing tests and do testing in more functional way
- fix matchers tests and add some handy matchers
- fix tests for exceptions
- fix API docs for mockify module
- fix docstring for matchers
- fix docstring for exc.py
- fix failing tests
- fix last remaining f"" format
- fix failing tests (forgot to save file)
- fix deploy job
- fix deploy job
- fix versioning scheme
- fix classifier
- fix version formatting

### Feat

- added quickstart guide and started doctesting using Sphinx
- added UnexpectedCall exception (partial, not yet tested)
- add examples in form of tests (first example, first test)
- add example with ProtocolReader class
- add ItemRepositoryFacade test example
- add tests for context managers
- add tests for remaining Mock functionality
- add missing tests for cardinality.py module
- add tutorial for creating mocks
- add tutorial for using mock factories
- add tutorial for using sessions
- add tutorial about creating mocks
- add tests to MockFactory class
- add patching modules tutorial
- add tests for Py3.8 and Py3.4 and add more classifiers

## 0.5.0 (2019-07-27)

### Fix

- fix clean task
- fix failing doctest in tutorial
- fix changelog

### Feat

- add regression task
- add module rename to changelog
- add build task for building all - docs and package
- add Namespace mock

## 0.4.0 (2019-07-24)

### Feat

- add strategies for dealing with uninterested calls

## 0.3.1 (2019-01-16)

### Feat

- add expecting property getting
- add docstring
- add UninterestedGetterCall and UninterestedSetterCall exceptions

## 0.2.1 (2019-01-05)

### Feat

- add description to sidebar
- add regression.sh file to wrap pytest
- add FunctionFactory utility
- add runtest.sh to scripts and reorganize scripts
- add tutorial chapter about FunctionFactory objects usage
- add missing docstring
- add CHANGELOG.txt

## 0.1.12 (2019-01-01)

Initial release.

