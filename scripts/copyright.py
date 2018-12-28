#!/usr/bin/env python

import os
import glob
import shutil
import argparse

_MARKER = '# ' + '-' * 75
_TEMPLATE =\
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


def insert_copyright(source, year, holder):

    def write_copyright(dst):
        dst.write(_TEMPLATE.format(
            marker=_MARKER, filename=source, year=year, holder=holder))

    def write_rest(src, dst):
        line = src.readline()
        while line:
            dst.write(line)
            line = src.readline()

    def process_file(src, dst):
        line = src.readline()
        if line:
            if line.startswith(_MARKER):
                line = src.readline()
                while not line.startswith(_MARKER):
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
        description='Tool for appending copyright notice to Python files')
    parser.add_argument('path', metavar='PATH', help='path to directory to look for *.py files')
    parser.add_argument('--holder', metavar='STRING', help='copyright holder')
    parser.add_argument('--year', type=int, metavar='NUMBER', help='copyright year')
    return parser.parse_args()


def main():
    args = parse_args()
    for filename in scan(args.path):
        insert_copyright(filename, args.year, args.holder)


if __name__ == '__main__':
    main()
