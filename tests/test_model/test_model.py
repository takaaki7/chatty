# -*- coding:utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime

from tests import mock_request, fix_matcher_rand

"""
test models.
"""

import pytest

from chatty.domain.model import (Session, )


@pytest.mark.usefixtures('my_init_db')
def test_user_location(mocker, monkeypatch):
    fix_matcher_rand(mocker)
    from chatty.domain.user_state import (
        User,
    )

    import requests
    mock_request(monkeypatch, requests)
    user1 = User('TEST-01')
    assert user1.has_location() == False
    # at TokyoTocho
    user1.current_longitude = 139.4130
    assert user1.has_location() == False
    user1.current_latitude = 35.4122
    assert user1.has_location() == True
    user2 = User('TEST-02')
    # at OsakaShiyakusho
    user2.current_longitude = 135.3008
    user2.current_latitude = 34.4138
    # about 400km distance between tokyo and osaka
    assert abs(user1.distance(user2) - 400) < 10


@pytest.mark.usefixtures('my_init_db')
def test_match_gender(mocker, monkeypatch):
    fix_matcher_rand(mocker)
    from chatty.domain.user_state import (
        User,
    )
    from chatty.domain.model.match import Language, MatchingQueue
    import requests
    mock_request(monkeypatch, requests)
    session = Session()
    english = (session.query(Language).get('en_US')
               or Language(id='en_US', name='English'))
    user = User('TEST-01')
    user.languages = [english]
    user.gender = "male"
    partner = User('TEST-02')
    partner.languages = [english]
    partner.gender = "female"
    partner.finding_genders = "male,female"

    user.finding_genders = "female"
    session.add(user)
    session.add(partner)
    session.commit()
    MatchingQueue.push(partner)
    assert MatchingQueue.match_partner(user) == partner
    MatchingQueue.remove(partner)
    user.partner = None

    MatchingQueue.push(partner)
    user.finding_genders = "male"
    assert MatchingQueue.match_partner(user) == None

    user.finding_genders = "male,female"
    assert MatchingQueue.match_partner(user) == partner
    user.partner = None
    MatchingQueue.remove(partner)

    MatchingQueue.push(partner)
    partner.finding_genders = "female"
    assert MatchingQueue.match_partner(user) == None

    user.gender = "undefined"
    assert MatchingQueue.match_partner(user) == None


@pytest.mark.usefixtures('my_init_db')
def test_match_last_matched(mocker, monkeypatch):
    fix_matcher_rand(mocker)
    from chatty.domain.user_state import (
        User,
    )
    from chatty.domain.model.match import Language, MatchingQueue

    import requests
    mock_request(monkeypatch, requests)
    session = Session()
    english = (session.query(Language).get('en_US')
               or Language(id='en_US', name='English'))
    user = User('TEST-01')
    user.languages = [english]
    partner = User('TEST-02')
    partner.languages = [english]

    session.add(user)
    session.add(partner)
    session.commit()
    MatchingQueue.push(partner)
    assert MatchingQueue.match_partner(user) == partner
    MatchingQueue.remove(partner)
    user.partner = None
    user.last_matched = partner.id
    MatchingQueue.push(partner)
    assert MatchingQueue.match_partner(user) == None

    user.last_matched = "other"
    assert MatchingQueue.match_partner(user) == partner


@pytest.mark.usefixtures('my_init_db')
def test_user_default_languages(mocker, monkeypatch, caplog):
    fix_matcher_rand(mocker)
    from chatty.domain.model.match import (
        User,
        Language
    )

    # session
    session = Session()

    english = (session.query(Language).get('en_US')
               or Language(id='en_US', name='English'))
    ar = (session.query(Language).get('ar_AR')
          or Language(id='ar_AR', name='Arabic'))

    user = User('TEST-01')

    assert set(user.languages) == set([english])

    monkeypatch.setattr(User, 'locale', 'xx_XX')

    user = User('TEST-02')
    assert set(user.languages) == set([english])

    monkeypatch.setattr(User, 'locale', 'ar_AR')

    user = User('TEST-03')
    assert set(user.languages) == set([ar])


@pytest.mark.usefixtures('my_init_db')
def test_match(monkeypatch, caplog):
    from chatty.domain.model.match import (
        Match
    )

    # session
    time = datetime.utcnow()
    Match.create("test1", "test2", time, 10, 0)
    m1 = Match.get("test1")
    m2 = Match.get("test2")
    assert m1 == m2
    assert m1.founder_id == "test1"
    assert m1.waiter_id == "test2"
    assert m1.waited_at == time
    assert m1.founder_used_points == 10
    assert m1.waiter_used_points == 0
