#!/usr/bin/env python3

from setuptools import setup

setup(
        name='py-gpsd2',
        version='0.1.0',
        packages=['gpsd2'],
        url='https://github.com/hatsunearu/py-gpsd2',
        license='MIT',
        author='Martijn Braam', 'hatsunearu',
        author_email='me@hatsunearu',
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
