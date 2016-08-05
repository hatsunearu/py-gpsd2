#!/usr/bin/env python3

from setuptools import setup

setup(
        name='gpsd-py3',
        version='0.2.0',
        packages=['gpsd'],
        url='https://github.com/MartijnBraam/gpsd-py3',
        license='MIT',
        author='Martijn Braam',
        author_email='martijn@brixit.nl',
        description='Python 3 library for working with gpsd',
        keywords=["gps", "gpsd"],
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Development Status :: 4 - Beta",
            "Operating System :: POSIX :: Linux",
            "License :: OSI Approved :: MIT License"
        ],
)
