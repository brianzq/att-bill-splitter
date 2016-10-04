# -*- coding:utf-8 -*-
"""Setup for att-bill-splitter."""

from setuptools import find_packages, setup


setup(
    name='att-bill-splitter',
    description='Parse AT&T bill and split wireless charges among users.',
    version='0.1',
    author='Brian Zhang',
    auther_email='leapingzhang@gmail.com',
    install_requires=[
        'peewee>=2.8.4',
        'python-slugify>=1.2.1',
        'selenium>=2.53.6',
        'Unidecode>=0.4.19'
    ],
    packages=find_packages(),
    extras_require={
        'testing': [
            'pytest>=2.9.2'
        ]
    },
    entry_points={
        'console_scripts': [
            'run-split-bill=attbillsplitter.entrypoints:run_split_bill'
        ],
    },
    zip_safe=False
)
