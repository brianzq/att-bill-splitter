# -*- coding:utf-8 -*-
"""Entrypoints for att-bill-splitter:
    * split-bill
"""


def split_bill():
    """Parse AT&T bill and split wireless charges among users."""
    from attbillsplitter.main import run_split_bill
    return run_split_bill()


def print_summary():
    """Print wireless monthly summary among users."""
    from attbillsplitter.services import run_print_summary
    return run_print_summary()


def print_details():
    """Print wireless monthly details among users."""
    from attbillsplitter.services import run_print_details
    return run_print_details()


def notify_users():
    """Print wireless monthly details among users."""
    from attbillsplitter.services import run_notify_users
    return run_notify_users()


def init_twilio():
    """Initialize twilio credentials."""
    from attbillsplitter.utils import initialize_twiolio
    return initialize_twiolio()


def init_payment_msg():
    """Initialize twilio credentials."""
    from attbillsplitter.utils import initialize_payment_msg
    return initialize_payment_msg()
