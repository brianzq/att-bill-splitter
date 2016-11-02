# -*- coding:utf-8 -*-
"""Exceptions used in main module."""

from peewee import IntegrityError


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


__all__ = ['ConfigError', 'UrlError', 'LoginError', 'ParsingError',
           'CalculationError', 'IntegrityError']
