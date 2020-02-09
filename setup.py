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
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
