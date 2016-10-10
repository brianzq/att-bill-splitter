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
        'selenium>=2.40.0',
        'Unidecode>=0.4.19',
        'twilio>=5.6.0'
    ],
    packages=find_packages(),
    extras_require={
        'testing': [
            'pytest>=2.9.2'
        ]
    },
    entry_points={
        'console_scripts': [
            'run-split-bill=attbillsplitter.entrypoints:run_split_bill',
            'run-print-summary=attbillsplitter.entrypoints:run_print_summary',
            'run-print-details=attbillsplitter.entrypoints:run_print_details',
            'run-notify-users=attbillsplitter.entrypoints:run_notify_users',
        ],
    },
    zip_safe=False
)
