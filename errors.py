# -*- coding:utf-8 -*-

"""Custom Exceptions used in main module."""

from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException
)

from peewee import IntegrityError


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
