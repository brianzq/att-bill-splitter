# -*- coding:utf-8 -*-
"""Entrypoints for att-bill-splitter:
    * split-bill
"""


def run_split_bill():
    """Parse AT&T bill and split wireless charges among users."""
    from attbillsplitter.main import run_split_bill
    return run_split_bill()


def run_print_summary():
    """Print wireless monthly summary among users."""
    from attbillsplitter.services import run_print_summary
    return run_print_summary()


def run_print_details():
    """Print wireless monthly details among users."""
    from attbillsplitter.services import run_print_details
    return run_print_details()


def run_notify_users():
    """Print wireless monthly details among users."""
    from attbillsplitter.services import run_notify_users
    return run_notify_users()
