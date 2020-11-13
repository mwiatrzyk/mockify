# ---------------------------------------------------------------------------
# setup.py
#
# Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import setuptools


with open("README.md", "r") as fd:
    long_description = fd.read()


def version_scheme(version):
    if not version.distance:
        return str(version.tag)
    major, minor, build = str(version.tag).split('.')
    return "{}.{}.{}".format(major, minor, int(build)+1)


def local_scheme(version):
    if not version.distance:
        return ''
    return "rc{}".format(version.distance)


setuptools.setup(
    name="mockify",
    use_scm_version={
        'write_to': 'mockify/_version.py',
        'version_scheme': version_scheme,
        'local_scheme': local_scheme
    },
    setup_requires=['setuptools_scm'],
    author="Maciej Wiatrzyk",
    author_email="maciej.wiatrzyk@gmail.com",
    description="Mocking library for Python inspired by Google Mock C++ mocking toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://mockify.readthedocs.io/",
    packages=setuptools.find_packages(exclude=["docs", "tests*"]),
    keywords="mock, mocking, testing, toolkit, library, framework",
    python_requires=">=3.6, <4",
    project_urls={
        'Bug Reports': "https://gitlab.com/zef1r/mockify/-/issues",
        'Source': "https://gitlab.com/zef1r/mockify",
        'Documentation': "https://mockify.readthedocs.io/",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
    ],
)
