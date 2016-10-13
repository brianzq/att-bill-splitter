# -*- coding:utf-8 -*-
"""Utility methods."""

import configparser
import os

CONFIG_PATH = os.path.expanduser('~/.attbillsplitter.conf')
PAGE_LOADING_WAIT_S = 10


def load_project_path():
    """Load project path from ~/.attbillsplitter.conf"""
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    try:
        return config['settings']['project_path']
    except KeyError:
        print('Config files not found. Please reinstall package by running '
              'python3 setup.py install')


PROJECT_PATH = load_project_path()
CHROMEDRIVER_PATH = os.path.join(PROJECT_PATH, 'chromedriver')
DATABASE_PATH = os.path.join(PROJECT_PATH, 'att_bill.db')
LOG_PATH = os.path.join(PROJECT_PATH, 'notif_history.log')


def initialize_twiolio():
    """Initialize twilio credentials from command line input and save in
    config file.
    """
    number = input('Twilio Number (e.g. +11234567890): ')
    account_sid = input('Twilio Account SID: ')
    auth_token = input('Twilio Authentication Token: ')
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    config['twilio'] = {}
    config['twilio']['number'] = number
    config['twilio']['account_sid'] = account_sid
    config['twilio']['auth_token'] = auth_token
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)
    print('\U00002705  Twilio account added.')


def load_twilio_config():
    """Load twilio credentials. Prompt to initialize if not yet initialized.
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    # initialize twilio if not yet initialized
    if 'twilio' not in config.sections():
        initialize_twiolio()
        config.read(CONFIG_PATH)

    twilio = config['twilio']
    return (twilio['number'], twilio['account_sid'], twilio['auth_token'])


def initialize_payment_msg():
    """Initialize payment message to be appended to the charging details
    before sending to users (generally a mesaage to tell users how to pay you).
    """
    prompt_msg = ('You can enter a short message to put after the charge '
                  'details to send to your users. (For example, letting your '
                  'users know how to pay you)\n-> ')
    message = input(prompt_msg)
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    config['message'] = {}
    config['message']['payment'] = message
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)
    print('\U00002705  Payment message saved.')


def load_payment_msg():
    """Load payment message. Prompt to initialize if not yet initialized."""
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    # initialize twilio if not yet initialized
    if ('message' not in config.sections() or
            'payment' not in config['message']):
        initialize_payment_msg()
        config.read(CONFIG_PATH)

    else:
        message = config['message']['payment']
        reset = input('\U00002753  Do you want to keep using the following '
                      'message: \n{}\n(y/n)? '.format(message))
        if reset in ('n', 'N', 'no', 'No', 'No'):
            initialize_payment_msg()
            config.read(CONFIG_PATH)
    return config['message']['payment']
