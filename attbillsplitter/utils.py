# -*- coding:utf-8 -*-
"""Utility methods."""

import configparser
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
# TWILIO_CONFIG_PATH = os.path.join(current_dir, 'att_twilio.ini')
# MSG_CONFIG_FILE_PATH = os.path.join(current_dir, 'att_message.ini')
TWILIO_CONFIG_PATH = os.path.expanduser('~/.att_twilio.ini')
MSG_CONFIG_FILE_PATH = os.path.expanduser('~/.att_message.ini')
PAGE_LOADING_WAIT_S = 10


def initialize_twiolio():
    """Initialize twilio credentials from command line input and save in
    config file.
    """
    number = input('Twilio Number (e.g. +11234567890): ')
    account_sid = input('Twilio Account SID: ')
    auth_token = input('Twilio Authentication Token: ')
    config = configparser.ConfigParser()
    config['twilio'] = {}
    config['twilio']['number'] = number
    config['twilio']['account_sid'] = account_sid
    config['twilio']['auth_token'] = auth_token

    with open(TWILIO_CONFIG_PATH, 'w') as configfile:
        config.write(configfile)
    print('Twilio account initialized.')


def load_twilio_config():
    """Load twilio credentials. Prompt to initialize if not yet initialized.
    """
    config = configparser.ConfigParser()
    config.read(TWILIO_CONFIG_PATH)
    # initialize twilio if not yet initialized
    if 'twilio' not in config.sections():
        initialize_twiolio()
        config.read(TWILIO_CONFIG_PATH)

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
    config['message'] = {}
    config['message']['payment'] = message
    with open(MSG_CONFIG_FILE_PATH, 'w') as configfile:
        config.write(configfile)
    print('Payment message saved.')


def load_payment_msg():
    """Load payment message. Prompt to initialize if not yet initialized."""
    config = configparser.ConfigParser()
    config.read(MSG_CONFIG_FILE_PATH)
    # initialize twilio if not yet initialized
    if ('message' not in config.sections() or
            'payment' not in config['message']):
        initialize_payment_msg()
        config.read(MSG_CONFIG_FILE_PATH)

    return config['message']['payment']
