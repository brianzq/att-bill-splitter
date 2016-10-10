# -*- coding:utf-8 -*-
"""Test cases for att-bill-splitter."""

import datetime as dt
from attbillsplitter.main import get_start_end_date


def test_get_start_end_date():
    billing_cycle_name = 'Mar 15 - Apr 14, 2016'
    start_date = dt.date(2016, 3, 15)
    end_date = dt.date(2016, 4, 14)
    assert get_start_end_date(billing_cycle_name) == (start_date, end_date)
