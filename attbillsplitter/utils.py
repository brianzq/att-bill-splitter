# -*- coding:utf-8 -*-
"""Utility methods"""

from __future__ import print_function, unicode_literals
from builtins import input
try:
    import configparser
except:
    import ConfigParser as configparser
import os
import sys
import warnings

CONFIG_PATH = os.path.expanduser('~/.attbillsplitter.conf')
PAGE_LOADING_WAIT_S = 10
DATABASE_PATH = 'att_bill.db'
LOG_PATH = 'notif_history.log'
warnings.simplefilter('ignore')


def initialize_twiolio():
    """Initialize twilio credentials from command line input and save in
    config file.

    :returns: None
    """
    number = input('Twilio Number (e.g. +11234567890): ')
    account_sid = input('Twilio Account SID: ')
    auth_token = input('Twilio Authentication Token: ')
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    if config.remove_section('twilio'):
        print('\U00002B55  Old twilio credentials removed.')

    config.add_section('twilio')
    config.set('twilio', 'number', number)
    config.set('twilio', 'account_sid', account_sid)
    config.set('twilio', 'auth_token', auth_token)
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)
    print('\U00002705  New twilio account added.')


def load_twilio_config():
    """Load twilio credentials. Prompt to initialize if not yet initialized.

    :returns: a tuple of twilio number, sid and auth token
    :rtype: tuple
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    # initialize twilio if not yet initialized
    if 'twilio' not in config.sections():
        initialize_twiolio()
        config.read(CONFIG_PATH)

    number = config.get('twilio', 'number')
    account_sid = config.get('twilio', 'account_sid')
    auth_token = config.get('twilio', 'auth_token')
    return (number, account_sid, auth_token)


def initialize_payment_msg():
    """Initialize payment message to be appended to the charging details
    before sending to users (generally a mesaage to tell users how to pay you).

    :returns: None
    """
    prompt_msg = ('You can enter a short message to put after the charge '
                  'details to send to your users. (For example, letting your '
                  'users know how to pay you)\n-> ')
    message = input(prompt_msg)
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    if config.remove_section('message'):
        print('\U00002B55  Old payment message removed.')
    config.add_section('message')
    config.set('message', 'payment', message)
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)
    print('\U00002705  New payment message saved.')


def load_payment_msg():
    """Load payment message. Prompt to initialize if not yet initialized.

    :returns: payment message cached in config file
    :rtype: str
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    # initialize twilio if not yet initialized
    if ('message' not in config.sections() or
            'payment' not in [t for (t, _) in config.items('message')]):
        initialize_payment_msg()
        config.read(CONFIG_PATH)

    else:
        message = config.get('message', 'payment')
        prompt = ('\U00002753  Do you want to keep using the following '
                  'message: \n{}\n(y/n)? '.format(message))
        try:
            # python3
            reset = input(prompt)
        except UnicodeEncodeError:
            # python2
            reset = input(prompt.encode(sys.stdout.encoding))
        if reset in ('n', 'N', 'no', 'No', 'No'):
            initialize_payment_msg()
            config.read(CONFIG_PATH)
    return config.get('message', 'payment')
