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

logger = logging.getLogger(__name__)

_root_dir = os.path.abspath(os.path.dirname(__file__))


def _configure_logger(verbosity):
    if verbosity == 0:
        logging.basicConfig(level=logging.ERROR)
    elif verbosity == 1:
        logging.basicConfig(level=logging.WARNING)
    elif verbosity == 2:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.DEBUG)


@invoke.task(incrementable=['verbosity'])
def update_copyright(_, verbosity=0):
    """Update copyright notice in license, source code and documentation
    files."""
    year_started = 2018
    year_current = datetime.now().year
    copyright_holder = 'Maciej Wiatrzyk'

    def scan(pattern, ignore=None):
        for item in glob.iglob(os.path.join('**', pattern), recursive=True):
            if ignore is None or not ignore(item):
                stats = os.stat(item)
                if stats.st_size > 0:
                    yield item

    def load_template(path):
        return open(path).read().split('\n')

    def format_template(lines, path):
        return '\n'.join(lines).format(
            filename=path,
            year="{} - {}".format(year_started, year_current),
            holder=copyright_holder
        )

    def update_files(pattern, ignore=None):
        template = load_template(
            os.path.join(
                _root_dir, 'data', 'templates', 'heading',
                "{}.txt".format(pattern[2:])
            )
        )
        marker_line = template[0]
        logger.info("Updating copyright notice in %s files...", pattern)
        for src_path in scan(pattern, ignore=ignore):
            dst_path = src_path + '.new'
            with open(src_path) as src:
                with open(dst_path, 'w') as dst:
                    dst.write(format_template(template, src_path))
                    line = src.readline()
                    if line.startswith(marker_line):
                        line = src.readline()
                        while not line.startswith(marker_line):
                            line = src.readline()
                        line = src.readline()
                    while line:
                        dst.write(line)
                        line = src.readline()
            shutil.move(dst_path, src_path)
            logger.debug("%s - OK", src_path)
        logger.info('Done.')

    def update_license():
        logger.info('Updating copyright notice in LICENSE...')
        with open(
            os.path.join(_root_dir, 'data', 'templates', 'LICENSE.txt')
        ) as src:
            with open(os.path.join(_root_dir, 'LICENSE'), 'w') as dst:
                dst.write(
                    src.read().format(
                        year="{} - {}".format(year_started, year_current),
                        holder=copyright_holder
                    )
                )
        logger.info('Done.')

    _configure_logger(verbosity)
    update_files(
        '*.py', ignore=lambda path: 'docs' in path or 'setup.py' in path
    )
    update_files('*.rst', ignore=lambda path: 'README' in path)
    update_license()


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
