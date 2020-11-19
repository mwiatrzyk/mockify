# ---------------------------------------------------------------------------
# tasks.py
#
# Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import invoke

import mockify


@invoke.task
def test_unit(ctx):
    """Run unit tests."""
    ctx.run('pytest tests/')


@invoke.task
def test_docs(ctx):
    """Run documentation tests."""
    ctx.run('sphinx-build -M doctest docs/source docs/build')


@invoke.task(test_unit, test_docs)
def test(_):
    """Run all tests."""


@invoke.task
def coverage(ctx):
    """Run code coverage check."""
    ctx.run(
        'pytest tests/ --cov=mockify --cov-fail-under=96 --cov-report=html:reports/coverage/html --cov-report=xml:reports/coverage/coverage.xml'
    )


@invoke.task
def lint_code(ctx):
    """Run linter on source files."""
    ctx.run(
        'pylint -f colorized --fail-under=9.0 mockify scripts tasks.py setup.py'
    )


@invoke.task
def lint_tests(ctx):
    """Run linter on test files."""
    args = ['pylint tests -f colorized --fail-under=9.0']
    args.extend(
        [
            '-d missing-module-docstring',
            '-d missing-class-docstring',
            '-d missing-function-docstring',
            '-d attribute-defined-outside-init',
            '-d too-few-public-methods',
            '-d too-many-public-methods',
            '-d no-self-use',
            '-d line-too-long',
        ]
    )
    ctx.run(' '.join(args))


@invoke.task(lint_code, lint_tests)
def lint(_):
    """Run all linters."""


@invoke.task(test, coverage, lint)
def check(_):
    """Run all code quality checks."""


@invoke.task
def tox(ctx, parallel=False, env=None):
    """Run all code quality checks using tox.

    This will by default run checks on all supported Python versions.

    -p, --parallel
        If set, all environments will be tested simultaneously, with a level
        of concurrency up to available CPU cores

    -e, --env
        Run tox with specified environment only, f.e. py36
    """
    args = ['tox']
    if parallel:
        args.append('-p')
    if env:
        args.append('-e {}'.format(env))
    ctx.run(' '.join(args))


@invoke.task
def fix_formatting(ctx):
    """Run code formatting tools."""
    ctx.run(
        'autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables --expand-star-imports mockify tests scripts tasks.py'
    )
    ctx.run('isort --atomic mockify tests scripts tasks.py')
    ctx.run('yapf -i --recursive --parallel mockify tests scripts tasks.py')


@invoke.task
def fix_license(ctx):
    """Update LICENSE file and license preambles in source files."""
    ctx.run(
        'scripts/licenser/licenser.py . --released={released} --author="{author}" -i "*.py" -i "*.rst"'
        .format(released=mockify.__released__, author=mockify.__author__)
    )


@invoke.task(fix_formatting, fix_license)
def fix(_):
    """Run all code fixers."""


@invoke.task
def build_docs(ctx):
    """Build Sphinx documentation."""
    ctx.run('sphinx-build -M html docs/source docs/build')


@invoke.task
def build_pkg(ctx):
    """Build distribution package."""
    ctx.run('python setup.py sdist bdist_wheel')


@invoke.task(build_docs, build_pkg)
def build(_):
    """Build all."""


@invoke.task
def validate_tag(ctx, tag):
    """Check CHANGELOG.md and mockify/__init__.py agains given tag."""
    ctx.run('scripts/tag.py -c {}'.format(tag))


@invoke.task(fix)
def release(ctx, tag_or_version):
    """Run code fixers and update version in library code.

    This task should be run just before committing the last changes before
    next release. `tag_or_version` should contain version library will
    receive in PyPI. This can later be verified in CI with `validate-tag`
    task.
    """
    ctx.run('scripts/tag.py {}'.format(tag_or_version))


@invoke.task(build_pkg)
def deploy_test(ctx):
    """Build and deploy library to test PyPI."""
    ctx.run(
        'twine upload --repository-url https://test.pypi.org/legacy/ dist/*'
    )


@invoke.task(build_pkg)
def deploy_prod(ctx):
    """Deploy library to production PyPI."""
    ctx.run('twine upload dist/*')


@invoke.task
def clean(ctx):
    """Clean working directory."""
    ctx.run('find . -name "*.pyc" -delete')
    ctx.run('find . -type d -name "__pycache__" -empty -delete')
    ctx.run('rm -rf docs/build')
    ctx.run('rm -rf build dist')
    ctx.run('rm -rf *.egg-info')
    ctx.run('rm -rf .eggs')
    ctx.run('rm -rf reports')
