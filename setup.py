#!/usr/bin/env python
from setuptools import setup

import tombstones

setup(
    name='django-tombstones',
    version=tombstones.__version__,
    description='Unintrusive soft-delete for django',
    long_description='',
    author='Nicholas Wolff',
    author_email='nwolff@gmail.com',
    url=tombstones.__URL__,
    download_url='https://pypi.python.org/pypi/django-tombstones',
    packages=[
        'tombstones',
        'tombstones.migrations',
    ],
    install_requires=[
        'Django>=1.7',
    ],
    license=tombstones.__licence__,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
    ],
)
