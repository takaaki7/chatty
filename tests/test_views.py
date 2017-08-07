# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import pytest
from mock import MagicMock

from chatty import server
from chatty.domain.model import Session
from chatty.domain.model.match import User
from chatty.libs import uidcrypt, tokener
from tests import assert_button, BetterTestApp


@pytest.mark.usefixtures('my_init_db')
def test_login_redirect(monkeypatch):
    app = BetterTestApp(server.app)
    from chatty.util import fb
    mocktokencheck = MagicMock(
        return_value=({"app_id": "dummy", "user_id": 123456}, "tokentoken"))
    monkeypatch.setattr(fb, "login_redirect_token_check", mocktokencheck)
    monkeypatch.setattr(fb, "profile_detail", MagicMock(return_value={
        'age_range': {"min": 18, "max": 21}}))
    uidenc = uidcrypt.encryptuid("1878285869108664")
    s = Session()
    s.add(User(1878285869108664))
    s.commit()
    s.close()
    tok = tokener.gen_token("1878285869108664", tokener.NS_LOGIN)
    r = app.get(
        "/bot/fb/signin_redirect?uid={}&state={}#tototoken".format(
            uidenc, tok))

    assert r.status_int == 200
    u = User.get("1878285869108664")
    assert u.id == "1878285869108664"
    assert u.fb_id == "123456"
    assert u.age_min == 18
    assert u.age_max == 21
    assert u.signup_date is not None


@pytest.mark.usefixtures('my_init_db')
def test_login_failed(monkeypatch):
    app = BetterTestApp(server.app)
    from chatty.util import fb
    mocksend = MagicMock()
    monkeypatch.setattr(fb, "send_data", mocksend)
    uid = uidcrypt.encryptuid("1878285869108664")
    app.get("/bot/fb/signin_redirect?uid={}&state={}#tototoken".format(
        uid, "dummy"), status=400)
    assert mocksend.call_count == 0

    s = Session()
    s.add(User(1878285869108664))
    s.commit()
    s.close()

    app.get(
        "/bot/fb/signin_redirect?uid={}&state={}#tototoken".format(
            uid, "dummy"), status=400)

    assert mocksend.call_count == 1
    assert_button(mocksend.call_args_list[0][0][0], "1878285869108664",
                  "Please log in with",
                  [fb.web_button("", "www.facebook.com/v2.8/dialog/oauth", "",
                                 "")])

# cannot assert some change happened here because it's threaded and async.
