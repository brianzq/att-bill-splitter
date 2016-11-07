# -*- coding:utf-8 -*-
"""Database and Data models for att-bill-splitter."""

from peewee import *
from attbillsplitter.utils import DATABASE_PATH

db = SqliteDatabase(DATABASE_PATH)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    name = CharField()
    number = CharField()
    created_at = DateTimeField(constraints=[SQL("DEFAULT (datetime('now'))")])

    class Meta:
        indexes = (
            (('name', 'number'), True),
        )


class ChargeCategory(BaseModel):
    category = CharField(unique=True)
    text = CharField()
    created_at = DateTimeField(constraints=[SQL("DEFAULT (datetime('now'))")])


class ChargeType(BaseModel):
    type = CharField()
    text = CharField()
    charge_category = ForeignKeyField(ChargeCategory)
    created_at = DateTimeField(constraints=[SQL("DEFAULT (datetime('now'))")])

    class Meta:
        indexes = (
            (('type', 'charge_category'), True),
        )


class BillingCycle(BaseModel):
    name = CharField(unique=True)
    start_date = DateField(unique=True)
    end_date = DateField(unique=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT (datetime('now'))")])


class Charge(BaseModel):
    user = ForeignKeyField(User)
    charge_type = ForeignKeyField(ChargeType)
    billing_cycle = ForeignKeyField(BillingCycle)
    amount = FloatField()
    created_at = DateTimeField(constraints=[SQL("DEFAULT (datetime('now'))")])

    class Meta:
        indexes = (
            # create a unique on user, charge_type, billing_cycle
            (('user', 'charge_type', 'billing_cycle'), True),
        )


class MonthlyBill(BaseModel):
    user = ForeignKeyField(User, related_name='mb_user')
    billing_cycle = ForeignKeyField(BillingCycle,
                                    related_name='mb_billing_cycle')
    total = FloatField()
    created_at = DateTimeField(constraints=[SQL("DEFAULT (datetime('now'))")])
