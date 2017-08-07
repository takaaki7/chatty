# -*- coding:utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import datetime

import pytest
from mock import MagicMock

from chatty.domain import black_list
from chatty.domain.model.match import User, MatchingQueue, Match, MatchHistory
from chatty.domain.user_state import UserStateDelegate, UserContext
from tests import assert_button, assert_message_is, fix_matcher_rand


@pytest.mark.usefixtures('my_init_db')
def test_on_found_partner(mocker, monkeypatch):
    delegate = UserStateDelegate()
    fix_matcher_rand(mocker)

    user = User.create("test1", finding_genders="male,female", gender="male",
                       points=30)
    partner = User.create("test2", finding_genders="male,female",
                          gender="male", points=30)
    uc, pc = [UserContext(u) for u in [user, partner]]
    record = MatchingQueue(created_at=datetime.datetime.utcnow(),
                           finding_genders="male,female")
    delegate.on_found_partner(uc, pc, record)
    assert user.points == 30
    assert partner.points == 30
    assert Match.get("test1").founder_used_points == 0
    delegate.on_match_ended(uc, pc)

    user.finding_genders = "female"
    partner.gender = "female"
    delegate.on_found_partner(uc, pc, record)
    assert user.points == 20
    assert partner.points == 30
    assert Match.get("test1").founder_used_points == 10
    assert Match.get("test1").waiter_used_points == 0
    delegate.on_match_ended(uc, pc)

    delegate.on_found_partner(pc, uc, record)
    assert user.points == 20
    assert partner.points == 30
    record.finding_genders = "female"
    delegate.on_match_ended(uc, pc)

    delegate.on_found_partner(pc, uc, record)
    assert user.points == 10
    assert partner.points == 30
    assert Match.get("test1").founder_used_points == 0
    assert Match.get("test1").waiter_used_points == 10


@pytest.mark.usefixtures('my_init_db')
def test_on_try_search(mocker, monkeypatch):
    fix_matcher_rand(mocker)
    delegate = UserStateDelegate()
    uc = UserContext(User.create("test1", "male,female", "male", 30))
    us = uc.status
    from chatty.util import fb

    mocksend = MagicMock()
    monkeypatch.setattr(fb, "send_data", mocksend)
    assert delegate.on_try_search(us)
    assert mocksend.call_count == 0

    us.user.points = 0
    assert delegate.on_try_search(us)
    assert mocksend.call_count == 0

    us.user.finding_genders = "female"
    assert not delegate.on_try_search(us)
    assert mocksend.call_count == 1

    assert_button(mocksend.call_args_list[0][0][0], "test1",
                  "enough points", [
                      fb.web_button("", "/buy_points", "", "")
                  ])


@pytest.mark.usefixtures('my_init_db')
def test_on_try_search_on_banned(mocker, monkeypatch):
    fix_matcher_rand(mocker)
    delegate = UserStateDelegate()
    uc = UserContext(User.create("test1", "male,female", "male", 30))
    us = uc.status
    from chatty.util import fb

    mocksend = MagicMock()
    monkeypatch.setattr(fb, "send_data", mocksend)
    black_list.ban_user("test1")
    assert not delegate.on_try_search(us)
    assert mocksend.call_count == 1
    assert_message_is(mocksend.call_args_list[0][0][0], "test1",
                      "suspended")


@pytest.mark.usefixtures('my_init_db')
def test_on_match_record(mocker, monkeypatch):
    fix_matcher_rand(mocker)
    delegate = UserStateDelegate()
    user = User.get("test1")
    partner = User.get("test2")
    time = datetime.datetime.utcnow()
    record = MatchingQueue(created_at=time,
                           finding_genders="male,female")
    uc, pc = [UserContext(u) for u in [user, partner]]

    delegate.on_found_partner(uc, pc, record)
    m1 = Match.get("test1")
    assert m1.founder_id == "test1"
    assert m1.waiter_id == "test2"
    assert m1.founder_speech_count == 0
    assert m1.waiter_speech_count == 0
    assert m1.founder_used_points == 0
    assert m1.waiter_used_points == 0
    assert m1.waited_at == time
    assert m1.started_at > time

    m2 = Match.get("test2")
    assert m1 == m2

    uc = UserContext(user)
    pc = UserContext(partner)
    delegate.on_speak(uc)
    assert m1.founder_speech_count == 1
    assert m1.waiter_speech_count == 0

    delegate.on_match_ended(uc, pc)
    assert Match.get("test1") is None
    assert Match.get("test2") is None

    res = MatchHistory.get("test1")
    assert len(res) == 1
    assert res[0].founder_id == "test1"
    assert res[0].ended_by == "test1"


@pytest.mark.usefixtures('my_init_db')
def test_on_match_increment_speech(mocker, monkeypatch):
    fix_matcher_rand(mocker)
    delegate = UserStateDelegate()
    user = User.get("test1")
    partner = User.get("test2")
    time = datetime.datetime.utcnow()
    record = MatchingQueue(created_at=time,
                           finding_genders="male,female")
    uc, pc = [UserContext(u) for u in [user, partner]]

    delegate.on_found_partner(uc, pc, record)
    m1 = Match.get("test1")
    assert m1.founder_speech_count == 0
    assert m1.waiter_speech_count == 0

    delegate.on_speak(uc)
    assert m1.founder_speech_count == 1
    assert m1.waiter_speech_count == 0
    delegate.on_speak(uc)
    assert m1.founder_speech_count == 2
    assert m1.waiter_speech_count == 0

    delegate.on_speak(pc)
    assert m1.founder_speech_count == 2
    assert m1.waiter_speech_count == 1
    delegate.on_speak(pc)
    assert m1.founder_speech_count == 2
    assert m1.waiter_speech_count == 2


@pytest.mark.usefixtures('my_init_db')
def test_on_match_end(mocker, monkeypatch):
    fix_matcher_rand(mocker)
    delegate = UserStateDelegate()
    user = User.create("test1", finding_genders="female", gender="male",
                       points=30)
    partner = User.create("test2", finding_genders="female,male",
                          gender="female", points=30)
    time = datetime.datetime.utcnow()
    record = MatchingQueue(created_at=time,
                           finding_genders="male,female")
    uc, pc = [UserContext(u) for u in [user, partner]]
    delegate.on_found_partner(uc, pc, record)

    delegate.on_speak(uc)
    delegate.on_speak(uc)
    delegate.on_speak(pc)

    delegate.on_match_ended(uc, pc)
    assert Match.get("test1") is None
    assert Match.get("test2") is None

    res = MatchHistory.get("test1")
    assert len(res) == 1
    assert res[0].founder_id == "test1"
    assert res[0].waiter_id == "test2"
    assert res[0].founder_speech_count == 2
    assert res[0].waiter_speech_count == 1
    assert res[0].founder_used_points == 10
    assert res[0].waiter_used_points == 0
    assert res[0].waited_at == time
    assert res[0].ended_by == "test1"
    assert res[0].started_at > time
