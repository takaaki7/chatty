# -*- coding:utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import logging

import functools
import os
from chatty.domain.model import (Session, )
from logging import getLogger
logger=getLogger(__name__)
if os.getenv('DEBUG', 'False') == 'TRUE':
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

def session_scope(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        session = Session()
        try:
            return func(*args, **kwargs)
        except Exception as e:
            session.rollback()
            logger.exception("Failed in session scope {}".format(e.message))
            raise e
        finally:
            session.commit()
            session.close()

    return wrapper
