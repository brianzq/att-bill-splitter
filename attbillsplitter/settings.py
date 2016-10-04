#!/usr/bin/env python
"""Configs used in the main module."""

# twilio
twilio_number = '+13103128668'
twilio_account_sid = 'ACcfa45113ae5bfb96fb78afe54c8a9075'
twilio_auth_token = '358d0dd19d428769ae97cf99388d62e4'

# AT&T account credentials
username = 'cfnczq@att.net'
password = 'Zq199156'

# phonebook with names and numbers
# name and number should match with user info on AT&T website
# number in format of '123-456-7890'
phonebook = [
    ('QIANG ZHANG', '310-849-5586'),
    ('QIANG ZHANG', '213-379-3374'),
    ('WENYAN MIAO', '424-901-3196'),
    ('QIMING SHAO', '310-666-8391'),
    ('KAIYU CHEN', '310-721-2583'),
    ('JIA HE', '310-733-7105'),
    ('QIANG ZHANG', '408-386-4029'),
    ('QIANG ZHANG', '424-230-1207'),
    ('XU WU', '424-901-3008'),
    ('BAOLIN YI', '424-901-3063'),
]

# config
# number of seconds to wait for the billing page to load
# increase this number if your internet is slow
page_loading_wait_s = 10
