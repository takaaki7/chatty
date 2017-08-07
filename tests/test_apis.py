# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import pytest
from mock import MagicMock

from chatty import server
from chatty.domain import black_list
from chatty.domain.model import Session
from chatty.domain.model.match import User
from chatty.domain.model.points import PaymentSource, Payment
from chatty.libs import tokener
from chatty.libs import uidcrypt
from tests import BetterTestApp


@pytest.mark.usefixtures('my_init_db')
def test_ban_user(monkeypatch):
    app = BetterTestApp(server.app)
    from chatty.libs import slack
    mockpost = MagicMock()
    monkeypatch.setattr(slack, "post", mockpost)
    s = Session()
    s.add(User(1878285869108664))
    s.commit()
    s.close()
    tok = tokener.gen_token_invert("1878285869108664", tokener.NS_BAN_USER)
    r = app.get("/ban_user/" + tok + "/confirm")
    assert mockpost.call_count == 1
    assert black_list.is_banned("1878285869108664")
    assert r.status == '200 OK'


@pytest.mark.usefixtures('my_init_db')
def test_payments(monkeypatch):
    app = BetterTestApp(server.app)
    from chatty.libs import slack
    import stripe
    slackpost = MagicMock()
    mock_customer_create = MagicMock(return_value=MagicMock(id="customerid"))
    mock_charge_create = MagicMock(return_value=MagicMock(id="chargeid"))
    monkeypatch.setattr(slack, "post", slackpost)
    monkeypatch.setattr(stripe.Customer, "create", mock_customer_create)
    monkeypatch.setattr(stripe.Charge, "create", mock_charge_create)
    User.create("1878285869108664", fb_id="testfbid")
    uidenc = uidcrypt.encryptuid("1878285869108664")
    tok = tokener.gen_token("1878285869108664", tokener.NS_PAYMENT_SECOND)
    r = app.post_json("/" + uidenc + "/payments?access_token=" + tok,
                      {"token": "stripetoken",
                       "points": 500, "price": 495, "currency": "USD"})
    assert slackpost.call_count == 0
    assert mock_customer_create.call_count == 1
    assert mock_charge_create.call_count == 1
    assert User.get("1878285869108664").points == 520

    assert PaymentSource.get("testfbid").stripe_id == "customerid"
    assert len(Payment.get("testfbid")) == 1
    assert r.status == "200 OK"


@pytest.mark.usefixtures('my_init_db')
def test_payments_invalid_menu(monkeypatch):
    app = BetterTestApp(server.app)
    from chatty.libs import slack
    import stripe
    slackpost = MagicMock()
    mock_customer_create = MagicMock(return_value=MagicMock(id="customerid"))
    mock_charge_create = MagicMock(return_value=MagicMock(id="chargeid"))
    monkeypatch.setattr(slack, "post", slackpost)
    monkeypatch.setattr(stripe.Customer, "create", mock_customer_create)
    monkeypatch.setattr(stripe.Charge, "create", mock_charge_create)
    User.create("1878285869108664", fb_id="testfbid")
    uidenc = uidcrypt.encryptuid("1878285869108664")
    tok = tokener.gen_token("1878285869108664", tokener.NS_PAYMENT_SECOND)
    r = app.post_json("/" + uidenc + "/payments?access_token=" + tok,
                      {"token": "stripetoken",
                       "points": 500, "price": 5, "currency": "USD"},
                      status=400)
    assert slackpost.call_count == 0
    assert mock_customer_create.call_count == 0
    assert mock_charge_create.call_count == 0
    assert User.get("1878285869108664").points == 20

    assert PaymentSource.get("testfbid") is None
    assert len(Payment.get("testfbid")) == 0
    assert r.status == "400 Bad Request"
    assert "expiration" in r.json['text']


@pytest.mark.usefixtures('my_init_db')
def test_payments_invalid_token(monkeypatch):
    app = BetterTestApp(server.app)
    User.create("1878285869108664", fb_id="testfbid")
    uidenc = uidcrypt.encryptuid("1878285869108664")
    tok = tokener.gen_token("1878285869108664", tokener.NS_PAYMENT_SECOND)
    r = app.post_json(
        "/" + uidenc + "/payments?access_token=" + "invalidtoken",
        {"token": "stripetoken",
         "points": 500, "price": 5, "currency": "USD"},
        status=400)
    assert User.get("1878285869108664").points == 20

    assert PaymentSource.get("testfbid") is None
    assert len(Payment.get("testfbid")) == 0
    assert r.status == "400 Bad Request"
    assert "expiration of token" in r.json['text']
