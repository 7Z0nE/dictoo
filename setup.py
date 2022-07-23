#!/usr/bin/env python

from setuptools import setup
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

install_requires = []
tests_require = ['pytest']

setup(name='dictoo',
    version='1.0',
    description='Utilities for working with json-style datastructures.',
    author='Frederik Wegner',
    author_email='onlyknoppas@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/7Z0nE/dicty',
    packages=['dictoo'],
    python_requires=">=3.7",
	install_requires=install_requires,
	tests_require=tests_require,
    license_files=('LICENSE',),

)
