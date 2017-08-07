# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import pytest
from webtest import TestApp, AppError

from chatty import server
from chatty.domain.model.match import User, Language
from tests import mock_request


class BetterTestApp(TestApp):
    """A testapp that prints the body when status does not match."""

    def _check_status(self, status, res):
        if status is not None and status != res.status_int:
            raise AppError(
                "Bad response: %s (not %s)\n%s", res.status, status, res)
        super(BetterTestApp, self)._check_status(status, res)


@pytest.mark.usefixtures('my_init_db')
def test_post_settings(monkeypatch):
    import requests
    mock_request(monkeypatch, requests)
    app = BetterTestApp(server.app)
    res = app.post("/VVaEZ1RQh3EvlGJqj7m1NiD6oF3UrxAM8c1oeWh1UQ0=/settings", {
        "languages": ["en_US", "fr_FR"],
        "genders": ["male", "female"],
        "longitude": 139.11,
        "latitude": 35.11,
        "location_enabled": "true",
        "search_radius": 350
    })

    assert res.status == "200 OK"
    user = User.get("1183739191739808")
    assert user.languages[0] == Language.get("en_US")
    assert user.languages[1] == Language.get("fr_FR")
    assert len(user.languages) == 2
    assert user.finding_genders == "male,female"
    assert user.current_longitude == 139.11
    assert user.current_latitude == 35.11
    assert user.location_enabled == True
    assert user.search_radius == 350

    res = app.post("/VVaEZ1RQh3EvlGJqj7m1NiD6oF3UrxAM8c1oeWh1UQ0=/settings", {
        "languages": ["en_US"],
        "genders": ["male"],
        "location_enabled": "false",
    })
    user = User.get("1183739191739808")
    assert res.status == "200 OK"
    assert user.languages[0] == Language.get("en_US")
    assert len(user.languages) == 1
    assert user.finding_genders == "male"
    assert user.location_enabled == False


@pytest.mark.usefixtures('my_init_db')
def test_message_callback(monkeypatch):
    app = BetterTestApp(server.app)
    import requests
    mock_request(monkeypatch, requests)
    res = app.post_json("/bot/fb/callback",
                        {u'entry': [{u'id': u'1878285869108664',
                                     u'messaging': [
                                         {u'message': {
                                             u'mid': u'mid.$cAAb2vDmGvz1haB8LUlbNtnB5GBUd',
                                             u'seq': 998,
                                             u'text': u'a'},
                                             u'recipient': {
                                                 u'id': u'1878285869108664'},
                                             u'sender': {
                                                 u'id': u'1409602299103010'},
                                             u'timestamp': 1491273892690}],
                                     u'time': 1491273892877}],
                         u'object': u'page'})
    assert res.status_int == 200
    # cannot assert some change happened here because it's threaded and async.
