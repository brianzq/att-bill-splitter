# -*- coding:utf-8 -*-
"""Entrypoints for att-bill-splitter:
    * split-bill
"""


def run_split_bill():
    """Parse AT&T bill and split wireless charges among users."""
    from attbillsplitter.main import run_split_bill
    return run_split_bill()
