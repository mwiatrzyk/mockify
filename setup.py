import setuptools

with open("README.md", "r") as fd:
    long_description = fd.read()

setuptools.setup(
    name="mockify",
    #version='.'.join(str(x) for x in mockify.__version__),
    use_scm_version={
        'write_to': 'mockify/_version.py'
    },
    setup_requires=['setuptools_scm'],
    author="Maciej Wiatrzyk",
    author_email="maciej.wiatrzyk@gmail.com",
    description="Mocking library for Python inspired by Google Mock C++ mocking toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown; charset=UTF-8",
    url="https://mockify.readthedocs.io/",
    packages=setuptools.find_packages(exclude=["docs", "tests*"]),
    classifiers=[
        "Development Status :: 4-Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.4",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
    ],
)
