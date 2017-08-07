import os
import pytest
import redis

from chatty import config
from chatty.domain import model
from chatty.domain.model import match, points


@pytest.fixture()
def my_init_db():
    # cleaa test user.
    session = model.Session()
    session.query(match.User).delete()
    session.query(match.Match).delete()
    session.query(match.MatchHistory).delete()
    session.query(match.MatchingQueue).delete()
    session.query(points.MenuPrice).delete()
    session.query(points.Payment).delete()
    session.query(points.PaymentSource).delete()
    session.commit()
    with model.engine.connect() as con:
        con.execute(open(os.getcwd() + "/tests/data/menu_prices.sql").read())
    cli = redis.from_url(config.REDIS_URL)
    cli.flushdb()
