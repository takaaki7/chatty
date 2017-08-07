# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import pytest
from bottle import HTTPError
from mock import MagicMock

from chatty import Session
from chatty.domain.model.match import User
from chatty.domain.model.points import PaymentSource, Payment


@pytest.mark.usefixtures('my_init_db')
def test_payments(monkeypatch):
    from chatty.domain import payment
    from chatty.libs import slack
    import stripe
    mockpost = MagicMock()
    mock_customer_create = MagicMock(return_value=MagicMock(id="customerid"))
    mock_charge_create = MagicMock(return_value=MagicMock(id="chargeid1"))
    monkeypatch.setattr(slack, "post", mockpost)
    monkeypatch.setattr(stripe.Customer, "create", mock_customer_create)
    monkeypatch.setattr(stripe.Charge, "create", mock_charge_create)
    User.create("test1", fb_id="testfbid")
    assert User.get("test1").points == 20

    payment.pay_from_form("test1", "stripetoken", 500, 495, "USD")

    assert mock_customer_create.call_count == 1
    assert mock_charge_create.call_count == 1

    ps = PaymentSource.get("testfbid")
    assert ps.user_id == "testfbid"
    assert ps.stripe_id == "customerid"
    assert ps.created_at is not None
    payments = Payment.get("testfbid")
    assert len(payments) == 1
    assert payments[0].id == "chargeid1"
    assert payments[0].user_id == "testfbid"
    assert payments[0].stripe_user_id == "customerid"
    assert payments[0].points == 500
    assert payments[0].price == 495
    assert payments[0].currency == "usd"

    mock_charge_create().id = "chargeid2"
    payment.pay_from_form("test1", "stripetoken", 1500, 21383, "EGP")

    ps = PaymentSource.get("testfbid")
    assert ps.user_id == "testfbid"
    assert ps.stripe_id == "customerid"
    assert ps.created_at is not None
    payments = Payment.get("testfbid")
    assert len(payments) == 2
    assert payments[1].id == "chargeid2"
    assert payments[1].user_id == "testfbid"
    assert payments[1].stripe_user_id == "customerid"
    assert payments[1].points == 1500
    assert payments[1].price == 21383
    assert payments[1].currency == "egp"


@pytest.mark.usefixtures('my_init_db')
def test_payments_faild(monkeypatch):
    from chatty.domain import payment
    from chatty.libs import slack
    import stripe
    mockpost = MagicMock()
    mock_customer_create = MagicMock(return_value=MagicMock(id="customerid"))
    mock_charge_create = MagicMock(return_value=MagicMock(id="chargeid1"))
    monkeypatch.setattr(slack, "post", mockpost)
    monkeypatch.setattr(stripe.Customer, "create", mock_customer_create)
    monkeypatch.setattr(stripe.Charge, "create", mock_charge_create)
    session = Session()
    User.create("test1", fb_id="testfbid")
    session.commit()
    session.close()

    def assert_no_effect():
        assert User.get("test1").points == 20
        assert PaymentSource.get("testfbid") is None
        assert len(Payment.get("testfbid")) == 0

    User.get("test1").points = 3999

    with pytest.raises(HTTPError) as e:
        payment.pay_from_form("test1", "stripetoken", 500, 495, "USD")
        assert "Limit Exceeded" in e.message
    assert mock_customer_create.call_count == 0
    assert mock_charge_create.call_count == 0
    assert_no_effect()

    with pytest.raises(HTTPError) as e:
        payment.pay_from_form("test1", "stripetoken", 500, 4, "USD")
        assert "menu might be changed" in e.message
    assert mock_customer_create.call_count == 0
    assert mock_charge_create.call_count == 0
    assert_no_effect()

    with pytest.raises(HTTPError) as e:
        payment.pay_from_form("test1", "stripetoken", 500, 495, "other")
        assert "menu might be changed" in e.message
    assert mock_customer_create.call_count == 0
    assert mock_charge_create.call_count == 0

    mock_customer_create.side_effect = stripe.error.CardError("e", {}, 400)
    with pytest.raises(HTTPError) as e:
        payment.pay_from_form("test1", "stripetoken", 500, 495, "USD")
        assert payment.MESSAGE_CONTACT_CREDIT in e.message
    assert_no_effect()

    mock_customer_create.side_effect = None
    mock_charge_create.side_effect = stripe.error.CardError("e", {}, 400)
    with pytest.raises(HTTPError) as e:
        payment.pay_from_form("test1", "stripetoken", 500, 495, "USD")
        assert payment.MESSAGE_CONTACT_CREDIT in e.message
    assert_no_effect()
