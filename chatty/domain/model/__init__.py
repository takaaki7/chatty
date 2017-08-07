# -*- coding:utf-8 -*-
"""model."""

from __future__ import print_function
from __future__ import unicode_literals

from sqlalchemy import (
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)

from chatty import (
    config,
)
from chatty.util import cache

engine = create_engine(config.DATABASE_URL, echo=False)
Base = declarative_base()
metadata = Base.metadata
metadata.bind = engine

# database session
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


def create_tables():
    metadata.create_all(engine)


def drop_tables():
    metadata.drop_all(engine)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--initdb", default=False, action="store_true")

    cache.cacher.flush_all()
    if parser.parse_args().initdb:
        drop_tables()
