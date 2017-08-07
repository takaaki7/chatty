# -*- coding:utf-8 -*-
"""model."""

from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime

import pycountry as pycountry
from sqlalchemy import (
    Column,
    DateTime,
    String,
    Integer)
from sqlalchemy import and_

from chatty.domain.model import (Base, Session)


class PaymentSource(Base):
    __tablename__ = 'payment_sources'
    # app_scope_id
    user_id = Column(String, primary_key=True)
    stripe_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    def __init__(self, user_id, stripe_id):
        self.user_id = user_id
        self.stripe_id = stripe_id

    @classmethod
    def create(cls, appscopeid, stripe_id):
        return Session().merge(cls(appscopeid, stripe_id))

    @classmethod
    def get(cls, appscopeid):
        return Session().query(cls).get(appscopeid)


class Payment(Base):
    __tablename__ = 'payments'
    id = Column(String, primary_key=True)
    # app_scope_id
    user_id = Column(String)
    stripe_user_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    points = Column(Integer())
    price = Column(Integer())
    currency = Column(String(3))

    @classmethod
    def create(cls, id, appscopeid, stripe_user_id, points, price,
               currency):
        p = cls()
        p.id = id
        p.user_id = appscopeid
        p.stripe_user_id = stripe_user_id
        p.points = points
        p.price = price
        p.currency = currency
        return Session().merge(p)

    @classmethod
    def get(cls, appscopeid):
        return Session().query(cls).filter(cls.user_id == appscopeid).all()


# class PointsMenu(Base):
#     __tablename__ = 'points_menu'
#     points = Column(Integer, primary_key=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     valid = Column(Boolean, default=True)
#

class MenuPrice(Base):
    __tablename__ = 'menu_prices'
    # amount of smallest unit. (https://stripe.com/docs/currencies )
    # e.g. {amount:100,currency:USD}=100cent=1dollar.
    points = Column(Integer(), primary_key=True)
    currency = Column(String(3), primary_key=True)
    price = Column(Integer())
    created_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)

    @classmethod
    def is_valid(cls, points, price, currency):
        session = Session()
        return session.query(session.query(cls).filter(
            and_(
                cls.points == points,
                cls.price == price,
                cls.currency == currency.upper(),
                cls.ended_at.is_(None))).exists()).scalar()

    @classmethod
    def menu_for_currency(cls, currency):
        session = Session()
        return session.query(cls).filter(
            and_(cls.currency == currency.upper(),
                 cls.ended_at.is_(None))).order_by(cls.points).all()

    @classmethod
    def menu_for_country(cls, country):
        country_name = country or "United States"
        try:
            country = pycountry.countries.lookup(country_name)
        except LookupError:
            country = pycountry.countries.lookup("United States")
        currency = pycountry.currencies.get(numeric=country.numeric)
        menu = MenuPrice.menu_for_currency(currency.alpha_3)
        return menu,currency.alpha_3
