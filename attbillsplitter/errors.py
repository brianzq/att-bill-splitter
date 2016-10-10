# -*- coding:utf-8 -*-
"""Exceptions used in main module."""

from peewee import IntegrityError
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException
)


class BaseError(Exception):
    pass


class ConfigError(BaseError):
    pass


class UrlError(BaseError):
    pass


class LoginError(BaseError):
    pass


class ParsingError(BaseError):
    pass


class CalculationError(BaseError):
    pass


__all__ = ['NoSuchElementException', 'TimeoutException', 'WebDriverException',
           'ConfigError', 'UrlError', 'LoginError', 'ParsingError',
           'CalculationError', 'IntegrityError']
