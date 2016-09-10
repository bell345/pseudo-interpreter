#!/usr/bin/env python3

import ez_setup
ez_setup.use_setuptools(version="10")

from setuptools import setup, find_packages

from pseudo.version import APP_NAME, APP_VERSION

def read(filename):
    with open(filename) as fp:
        return fp.read()

setup(
    name=APP_NAME,
    version=APP_VERSION,
    packages=find_packages(),
    author="Thomas Bell",
    author_email="tom.aus@outlook.com",
    url="https://github.com/bell345/pseudo-interpreter",
    description="An interpreter for simple PASCAL-like pseudo code.",
    long_description=read("README.md"),
    install_requires=[
        "tabulate>=0.7.5"
    ],
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Other",
        "Topic :: Education",
        "Topic :: Software Development :: Interpreters"
    ],
    keywords="pseudo code interpreter repl language",
    entry_points={
        'console_scripts': [
            'pseudo=pseudo:main'
        ]
    }
)
