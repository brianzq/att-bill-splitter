# -*- coding:utf-8 -*-
"""Database and Data models for att-bill-splitter."""

from peewee import *
from peewee import SqliteDatabase

DATABASE = 'att_bill.db'
db = SqliteDatabase(DATABASE)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    name = CharField()
    number = CharField(unique=True)
    created_at = DateTimeField(constraints=[SQL("DEFAULT (datetime('now'))")])


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
    user = ForeignKeyField(User)
    total = FloatField()
    notified_at = DateTimeField()
    paid_at = DateTimeField()
    created_at = DateTimeField(constraints=[SQL("DEFAULT (datetime('now'))")])
