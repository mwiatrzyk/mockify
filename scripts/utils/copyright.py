#!/usr/bin/env python

import os
import glob
import shutil
import argparse

from datetime import datetime

YEAR_STARTED = 2018
COPYRIGHT_HOLDER = 'Maciej Wiatrzyk'
MARKER = '# ' + '-' * 75
TEMPLATE =\
"""{marker}
# {filename}
#
# Copyright (C) {year} {holder}
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
{marker}
"""


def scan(path):
    return iter(glob.glob(os.path.join(path, '**', '*.py'), recursive=True))


def insert_copyright(source):

    def write_copyright(dst):
        dst.write(TEMPLATE.format(
            marker=MARKER, filename=source,
            year="{} - {}".format(YEAR_STARTED, datetime.now().year),
            holder=COPYRIGHT_HOLDER))

    def write_rest(src, dst):
        line = src.readline()
        while line:
            dst.write(line)
            line = src.readline()

    def process_file(src, dst):
        line = src.readline()
        if line:
            if line.startswith(MARKER):
                line = src.readline()
                while not line.startswith(MARKER):
                    line = src.readline()
                write_copyright(dst)
                write_rest(src, dst)
            else:
                write_copyright(dst)
                dst.write('\n')
                dst.write(line)
                write_rest(src, dst)

    dest = "{}.new".format(source)
    with open(dest, 'w') as dst:
        with open(source) as src:
            process_file(src, dst)
    shutil.move(dest, source)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Tool for updating copyright notice in Python files')
    parser.add_argument('path', metavar='PATH', help='path to directory to look for *.py files')
    return parser.parse_args()


def main():
    args = parse_args()
    for filename in scan(args.path):
        insert_copyright(filename)


if __name__ == '__main__':
    main()
