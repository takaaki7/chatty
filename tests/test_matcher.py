import pytest

from chatty import Session
from chatty.domain import matcher
from chatty.domain.matcher import Matcher
from chatty.domain.model.match import User, Language
from tests import fix_matcher_rand, mock_request


def test_matcher():
    assert Matcher().randomnum != Matcher().randomnum
    matcher = Matcher(randomnum=1)
    assert matcher.randomnum == 1
    user1 = User.create("u1", finding_genders="female,male", gender="male")
    user2 = User.create("u2", finding_genders="female,male", gender="female")
    user3 = User.create("u3", finding_genders="female", gender="female")
    user4 = User.create("u4", finding_genders="female", gender="male")
    cache = {'my_langs': set([Language.get("en_US")])}
    assert not matcher.should_match(user1, user2, cache, False)
    assert not matcher.should_match(user2, user3, cache, False)
    assert not matcher.should_match(user1, user4, cache, False)

    matcher.randomnum = 0
    assert matcher.should_match(user1, user2, cache, False)
    assert matcher.should_match(user2, user3, cache, False)
    assert not matcher.should_match(user1, user3, cache, False)
    assert not matcher.should_match(user1, user4, cache, False)


@pytest.mark.usefixtures('my_init_db')
def test_match_location(mocker, monkeypatch):
    fix_matcher_rand(mocker)
    from chatty.domain.user_state import (
        User,
    )
    from chatty.domain.model.match import Language

    import requests
    mock_request(monkeypatch, requests)
    session = Session()
    english = (session.query(Language).get('en_US')
               or Language(id='en_US', name='English'))
    user1 = User('TEST-01')
    user1.languages = [english]
    user2 = User('TEST-02')
    user2.languages = [english]

    session.add(user1)
    session.add(user2)
    session.commit()
    cache = dict(my_langs=set([english]))
    mat = matcher.get()
    # default, both don't use location
    assert mat.should_match(user1, user2, cache, True)
    user1.location_enabled = True
    # user1 wanna use location but don't have, so ignore.
    # user2 doesn't care location. match.
    assert mat.should_match(user1, user2, cache, True)
    # at TokyoTocho
    user1.current_longitude = 139.4130
    user1.current_latitude = 35.4122
    assert not mat.should_match(user1, user2, cache, True)
    assert mat.should_match(user1, user2, cache, False)
    # at OsakaShiyakusho
    user2.current_longitude = 135.3008
    user2.current_latitude = 34.4138
    # user2 is in user1 radius 400, and user2 doesn't care radius
    assert mat.should_match(user1, user2, cache, True)
    user2.location_enabled = True
    assert mat.should_match(user1, user2, cache, True)

    user2.search_radius = 100
    assert not mat.should_match(user1, user2, cache, True)
    assert mat.should_match(user1, user2, cache, False)
    user1.current_longitude = 136.3008
    user1.current_latitude = 34.4138
    assert mat.should_match(user1, user2, cache, True)
