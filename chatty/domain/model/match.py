# -*- coding:utf-8 -*-
"""model."""

from __future__ import print_function
from __future__ import unicode_literals

import logging
from datetime import datetime, timedelta

from geopy.distance import great_circle
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    Table,
    Float,
    Integer,
    Boolean,
    orm,
    or_)
from sqlalchemy import and_
from sqlalchemy.orm import (
    relation,
    relationship,
)
from sqlalchemy.sql.expression import func

from chatty import (
    config,
)
from chatty.domain import matcher
from chatty.domain.model import (metadata, Base, Session, )
from chatty.util import fb

logger = logging.getLogger(__name__)
user_languages = Table(
    'user_languages', metadata, Column(
        'user_id', String, ForeignKey(
            'users.id', ondelete='CASCADE'), primary_key=True), Column(
        'language_id', String, ForeignKey(
            'languages.id', ondelete='CASCADE'), primary_key=True))

user_partners = Table(
    'user_partners', metadata,
    Column(
        'user_id', String, ForeignKey('users.id', ondelete='CASCADE'),
        unique=True, primary_key=True),
    Column(
        'partner_id', String, ForeignKey('users.id', ondelete='CASCADE'),
        unique=True, primary_key=True),
    ForeignKeyConstraint(
        ['partner_id', 'user_id'],
        ['user_partners.user_id', 'user_partners.partner_id'],
        ondelete='CASCADE', deferrable=True, initially='DEFERRED'),
    CheckConstraint('user_id <> partner_id'))


class User(Base):
    __tablename__ = 'users'

    # page scope id
    id = Column(String, primary_key=True)
    # app_scope_id
    fb_id = Column(String, index=True)
    gender = Column(String)
    finding_genders = Column(String, default="male,female")
    current_latitude = Column(Float)
    current_longitude = Column(Float)
    search_radius = Column(Integer, default=400)
    location_enabled = Column(Boolean, default=False)
    last_matched = Column(String)
    languages = relation('Language', secondary=user_languages)
    partner = relationship(
        'User', uselist=False,
        secondary='user_partners',
        primaryjoin='users.c.id==user_partners.c.user_id',
        secondaryjoin='users.c.id==user_partners.c.partner_id'
    )
    age_min = Column(Integer)
    age_max = Column(Integer)
    signup_date = Column(DateTime)
    last_matched_date = Column(DateTime)
    country = Column(String)
    city = Column(String)
    state = Column(String)
    fb_access_token = Column(String)
    points = Column(Integer)
    version = Column(String)
    locale = Column(String)

    matching_queue_item = relation('MatchingQueue', uselist=False)

    def __init__(self, user_id, fb_id=None):
        self.id = user_id
        self.fb_id = fb_id
        self.init_profile()

    @classmethod
    def create(cls, id, finding_genders="male,female", gender="male",
               points=20, fb_id=None, locale="en_US"):
        user = User(id)
        user.finding_genders = finding_genders
        user.fb_id = fb_id
        user.locale = locale
        user.gender = gender
        user.points = points
        Session().add(user)
        return User.get(id)

    @orm.reconstructor
    def init_on_load(self):
        self.init_profile()

    def init_profile(self):
        profile = None
        if self.points is None:
            self.points = 20
        if not self.finding_genders:
            self.finding_genders = "male,female"
        if not self.gender:
            # set "undefined" string for stop following api using
            profile = profile or fb.profile(self.id)
            self.gender = profile.get("gender", "undefined")
        if not self.locale:
            profile = profile or fb.profile(self.id)
            self.locale = profile.get("locale", "en_US")
        if not self.languages:
            if self.locale in config.ENABLED_LANGUAGES:
                l = self.locale
            else:
                l = "en_US"
            self.languages = [Language.get(l)]

    @classmethod
    def get(cls, user_id):
        session = Session()
        user = session.query(cls).get(user_id) or cls(user_id=user_id)
        session.add(user)
        return user

    @classmethod
    def exists(cls, user_id):
        session = Session()
        return session.query(
            session.query(cls).filter(cls.id == user_id).exists()).scalar()

    @classmethod
    def get_by_appscope(cls, appscopeid):
        return Session().query(cls).filter(cls.fb_id == appscopeid)[0]

    @classmethod
    def inactive_user(cls, now, limit, gender):
        return Session().query(cls).filter(
            and_(
                cls.last_matched_date < (now - timedelta(days=3)),
                cls.gender == gender,
                cls.partner == None)).order_by(func.random()).limit(limit)

    def has_location(self):
        lat = self.current_latitude is not None
        lon = self.current_longitude is not None
        return lat and lon

    def distance(self, u):
        return great_circle((self.current_latitude, self.current_longitude),
                            (u.current_latitude,
                             u.current_longitude)).kilometers


class MatchingQueue(Base):
    __tablename__ = 'matching_queue'

    user_id = Column(
        String, ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True)
    created_at = Column(DateTime, nullable=False)
    finding_genders = Column(String, nullable=True)

    user = relationship('User')

    @classmethod
    def match_partner(cls, user):

        cache = dict(my_langs=set(user.languages))
        session = Session()
        mat = matcher.get()
        for item in session.query(cls).order_by(cls.created_at).all():
            if mat.should_match(user, item.user, cache, False):
                user.last_matched_date = datetime.now()
                item.user.last_matched_date = datetime.now()
                return item.user

    @classmethod
    def push(cls, user):
        session = Session()
        item = MatchingQueue(
            user=user, created_at=datetime.now(),
            finding_genders=user.finding_genders)
        session.add(item)

    @classmethod
    def remove(cls, user):
        session = Session()
        q = session.query(cls).filter(cls.user_id == user.id)
        if q.count() > 0:
            ret = q[0]
            q.delete()
            return ret
        else:
            return None


class Language(Base):
    __tablename__ = 'languages'
    id = Column(String(5), primary_key=True)
    name = Column(String, nullable=False)

    @classmethod
    def get(cls, id_):
        session = Session()
        lang = session.query(cls).get(id_)
        return lang

    @classmethod
    def all(cls):
        session = Session()
        return session.query(cls).all()


class Match(Base):
    __tablename__ = 'matches'
    id = Column(Integer, primary_key=True, autoincrement=True)
    founder_id = Column(String, index=True)
    waiter_id = Column(String, index=True)
    founder_speech_count = Column(Integer, default=0)
    waiter_speech_count = Column(Integer, default=0)
    waited_at = Column(DateTime)
    started_at = Column(DateTime, default=datetime.utcnow)
    founder_used_points = Column(Integer)
    waiter_used_points = Column(Integer)

    @classmethod
    def create(cls, founder_id, waiter_id, waited_at, founder_used_points,
               waiter_used_points):
        session = Session()
        match = cls()
        match.founder_id = founder_id
        match.waiter_id = waiter_id
        match.waited_at = waited_at
        match.founder_used_points = founder_used_points
        match.waiter_used_points = waiter_used_points
        session.add(match)

    @classmethod
    def get(cls, user_id):
        ret = Session().query(cls).filter(
            or_(cls.founder_id == user_id,
                cls.waiter_id == user_id)).one_or_none()
        return ret

    @classmethod
    def incr_speak(cls, user_id):
        obj = cls.get(user_id)
        if obj is None:
            logger.warn("Why match doesn't exist:{}".format(user_id))
            return
        if obj.founder_id == user_id:
            obj.founder_speech_count = obj.founder_speech_count + 1
        else:
            obj.waiter_speech_count = obj.waiter_speech_count + 1

    @classmethod
    def find_and_end(cls, user_id):
        session = Session()
        obj = cls.get(user_id)
        if obj is not None:
            session.delete(obj)
        else:
            logger.warn("Why match doesn't exist:{}".format(user_id))
        return obj


class MatchHistory(Base):
    __tablename__ = 'match_histories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    founder_id = Column(String)
    waiter_id = Column(String)
    founder_speech_count = Column(Integer)
    waiter_speech_count = Column(Integer)
    waited_at = Column(DateTime)
    started_at = Column(DateTime)
    ended_by = Column(String)
    ended_at = Column(DateTime, default=datetime.utcnow)
    founder_used_points = Column(Integer)
    waiter_used_points = Column(Integer)

    @classmethod
    def create(cls, match, ended_by):
        if match is None:
            return
        session = Session()
        obj = cls()
        obj.founder_id = match.founder_id
        obj.waiter_id = match.waiter_id
        obj.founder_speech_count = match.founder_speech_count
        obj.waiter_speech_count = match.waiter_speech_count
        obj.waited_at = match.waited_at
        obj.started_at = match.started_at
        obj.founder_used_points = match.founder_used_points
        obj.waiter_used_points = match.waiter_used_points
        obj.ended_by = ended_by

        session.add(obj)

    @classmethod
    def get(cls, founder_id):
        return Session().query(cls).filter(cls.founder_id == founder_id).all()
