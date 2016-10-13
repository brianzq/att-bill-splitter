# -*- coding:utf-8 -*-
"""Setup for att-bill-splitter."""

import configparser
import os
from urllib import request
import zipfile
from setuptools import find_packages, setup
from setuptools.command.install import install

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMEDRIVER_ZIP_PATH = os.path.join(CURRENT_DIR, 'chromedriver.zip')
CHROMEDRIVER_PATH = os.path.join(CURRENT_DIR, 'chromedriver')
CONFIG_PATH = os.path.expanduser('~/.attbillsplitter.conf')


def save_config():
    """Save current path to config file."""
    config = configparser.ConfigParser()
    config['settings'] = {}
    config['settings']['project_path'] = CURRENT_DIR
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)


def download_chrome_driver():
    """Download chromedriver 2.24 for mac os from
    http://chromedriver.storage.googleapis.com/2.24/chromedriver_mac64.zip
    """
    url = ('http://chromedriver.storage.googleapis.com/2.24/'
           'chromedriver_mac64.zip')
    print('Start dowloading chromedriver...')
    req = request.urlopen(url)
    with open(CHROMEDRIVER_ZIP_PATH, 'wb') as f:
        f.write(req.read())
    print('chromedriver.zip downloaded.')


def unzip_chrome_driver():
    """Unzip chromedriver.zip."""
    # unzip
    print('Start installing chromedriver.zip...')
    zf = zipfile.ZipFile(CHROMEDRIVER_ZIP_PATH)
    with open(CHROMEDRIVER_PATH, 'wb') as f:
        f.write(zf.read('chromedriver'))
    # delete the .zip file
    os.remove(CHROMEDRIVER_ZIP_PATH)
    # change permission on the executable
    os.chmod(CHROMEDRIVER_PATH, 0o755)
    print('chromedriver installed.')
    print('chromedriver.zip deleted.')


class InstallChromedriver(install):
    """Customized setuptools install command - download and install
    chromedriver.
    """
    def run(self):
        download_chrome_driver()
        unzip_chrome_driver()
        save_config()
        install.do_egg_install(self)


setup(
    name='att-bill-splitter',
    description='Parse AT&T bill and split wireless charges among users.',
    version='0.1',
    author='Brian Zhang',
    author_email='leapingzhang@gmail.com',
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
    cmdclass={
        'install': InstallChromedriver
    },
    zip_safe=False
)
