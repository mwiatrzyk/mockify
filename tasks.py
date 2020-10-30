# ---------------------------------------------------------------------------
# tasks.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import glob
import logging
import os
import shutil
from datetime import datetime

import invoke

import mockify

logger = logging.getLogger(__name__)

_root_dir = os.path.abspath(os.path.dirname(__file__))


@invoke.task
def update_copyright(ctx):
    """Update copyright notice in license, source code and documentation
    files."""
    ctx.run(
        'scripts/licenser/licenser.py . --released={released} --author="{author}" --i "*.py" -i "*.rst"'.
        format(released=mockify.__released__, author=mockify.__author__))


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
    """A shortcut for building everything."""


@invoke.task
def test_unit(ctx):
    """Run unit tests."""
    ctx.run('pytest tests/')


@invoke.task
def test_cov(ctx, html=False):
    """Run tests and check coverage."""
    opts = ''
    if html:
        opts += ' --cov-report=html'
    ctx.run("pytest tests/ --cov=src/_mockify{}".format(opts))


@invoke.task
def lint(ctx):
    """Run static code analyzer."""
    ctx.run('pylint --fail-under=9.0 mockify')


@invoke.task
def test_docs(ctx):
    """Run documentation tests."""
    ctx.run('sphinx-build -M doctest docs/source docs/build')


@invoke.task(test_unit, test_docs)
def test(_):
    """Run all tests."""


@invoke.task
def adjust_code(ctx):
    """Run code adjusting tools."""
    ctx.run(
        'autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables --expand-star-imports mockify tests tasks.py'
    )
    ctx.run('isort --atomic mockify tests tasks.py')
    ctx.run('yapf -i --recursive --parallel mockify tests tasks.py')


@invoke.task()
def deploy(ctx, env):
    """Deploy library to given environment."""
    if env == 'test':
        ctx.run(
            'twine upload --repository-url https://test.pypi.org/legacy/ dist/*'
        )
    elif env == 'prod':
        ctx.run('twine upload dist/*')
    else:
        raise RuntimeError("invalid env: {}".format(env))


@invoke.task
def clean(ctx):
    """Clean working directory."""
    ctx.run('find . -name "*.pyc" -delete')
    ctx.run('find . -type d -name "__pycache__" -empty -delete')
    ctx.run('rm -rf docs/build')
    ctx.run('rm -rf build dist')
    ctx.run('rm -rf *.egg-info')


@invoke.task(build_docs, build_pkg, test)
def regression(_):
    """Run regression tests."""
