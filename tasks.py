# ---------------------------------------------------------------------------
# tasks.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------

import os
import glob
import shutil

from datetime import datetime

import invoke

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


@invoke.task
def update_copyright(c):
    """Update copyright notice in license, source code and documentation
    files."""
    year_started = 2018
    year_current = datetime.now().year
    copyright_holder = 'Maciej Wiatrzyk'

    def scan(pattern, ignore=None, nonempty=True):
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
            year=f"{year_started} - {year_current}",
            holder=copyright_holder)

    def update_files(pattern, ignore=None):
        template = load_template(os.path.join(ROOT_DIR, 'data', 'templates', 'heading', f'{pattern[2:]}.txt'))
        marker_line = template[0]
        print(f"Updating copyright notice in {pattern} files...")
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
            print(f"{src_path} - OK")
        print('Done.')

    def update_license():
        print('Updating copyright notice in LICENSE.txt...')
        with open(os.path.join(ROOT_DIR, 'data', 'templates', 'LICENSE.txt')) as src:
            with open(os.path.join(ROOT_DIR, 'LICENSE.txt'), 'w') as dst:
                dst.write(src.read().format(
                    year=f"{year_started} - {year_current}",
                    holder=copyright_holder
                ))
        print('Done.')

    update_files('*.py', ignore=lambda path: 'docs' in path or 'setup.py' in path)
    update_files('*.rst', ignore=lambda path: 'README' in path)
    update_license()
