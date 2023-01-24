#!/usr/bin/env python3

import setuptools

setuptools.setup(
    name='k6webserver',
    version='0.0.1',
    description='',
    long_description='',
    packages=['server'],
    install_requires=[
        'flask',
        'pytz',
    ],
)
