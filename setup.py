import setuptools

with open("README.rst", "r") as fd:
    long_description = fd.read()

setuptools.setup(
    name="mockify",
    version="0.1.1",
    author="Maciej Wiatrzyk",
    author_email="maciej.wiatrzyk@gmail.com",
    description="Mocking library for Python inspired by Google Mock C++ mocking toolkit",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://mockify.readthedocs.io/",
    packages=setuptools.find_packages(exclude=["tests",]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
