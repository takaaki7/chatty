# -*- coding:utf-8 -*-
"""model."""

from __future__ import print_function
from __future__ import unicode_literals

import logging
from datetime import datetime, timedelta
from operator import and_

from sqlalchemy import (
    Column,
    String,
    Boolean)
from sqlalchemy import DateTime
from sqlalchemy import Integer

from chatty.domain.model import (Base, Session)

logger = logging.getLogger(__name__)


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True, autoincrement=True)
    target_user = Column(String, index=True,nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean)

    @classmethod
    def notified_thesedays(cls, now, user_id):
        session = Session()
        return session.query(
            session.query(cls).filter(and_(
                cls.target_user == user_id,
                cls.created_at > (now - timedelta(days=3))
            )).exists()).scalar()

    @classmethod
    def create(cls, target_user, description, success):
        Session().add(cls(target_user=target_user, description=description,
                          success=success))
