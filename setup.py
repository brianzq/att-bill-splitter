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
        'twilio>=5.6.0',
        'click>=6.6'
    ],
    packages=find_packages(),
    extras_require={
        'testing': [
            'pytest>=2.9.2'
        ]
    },
    entry_points={
        'console_scripts': [
            'att-split-bill=attbillsplitter.entrypoints:split_bill',
            'att-print-summary=attbillsplitter.entrypoints:print_summary',
            'att-print-details=attbillsplitter.entrypoints:print_details',
            'att-notify-users=attbillsplitter.entrypoints:notify_users',
            'att-init-twilio=attbillsplitter.entrypoints:init_twilio',
            'att-init-payment-msg=attbillsplitter.entrypoints:init_payment_msg'
        ],
    },
    zip_safe=False
)
