# -*- coding:utf-8 -*-
"""Exceptions used in main module."""

from peewee import IntegrityError
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException
)


class BaseError(Exception):
    pass


class UrlError(BaseError):
    pass


class LoginError(BaseError):
    pass


class ParsingError(BaseError):
    pass


class CalculationError(BaseError):
    pass


__all__ = ['NoSuchElementException', 'TimeoutException', 'BaseError',
           'UrlError', 'LoginError', 'ParsingError', 'CalculationError',
           'IntegrityError']
