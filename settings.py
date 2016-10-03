#!/usr/bin/env python

"""Configs used in the main module."""

# twilio
twilio_number = 'your_twilio_number'
twilio_account_sid = 'your_twilio_api_key_here'
twilio_auth_token = 'your_twilio_auth_token'

# credentials
username = 'your_att_user_name'
password = 'your_att_password'

# phonebook with names and numbers
# name and number should match with user info on AT&T website
# number in format of '123-456-7890'
phonebook = [
    ('account_holder_name', 'account_holder_number'),
    ('user_1_name', 'user_1_number'),
    ('user_2_name', 'user_2_number'),
    ('user_3_name', 'user_3_number'),
    ('user_4_name', 'user_4_number'),
    ('user_5_name', 'user_5_number'),
    ('user_6_name', 'user_6_number'),
    ('user_7_name', 'user_7_number'),
    ('user_8_name', 'user_8_number'),
    ('user_9_name', 'user_9_number'),
]

# config
# number of seconds to wait for the billing page to load
# increase this number if the internet is slow
page_loading_wait_s = 10
