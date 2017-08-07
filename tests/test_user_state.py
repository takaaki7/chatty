# -*- coding:utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import logging

from mock import MagicMock

from chatty.domain.model.match import User
from chatty.domain.user_state import UserContext, NoSignUpIdleUserState
from chatty.libs import action
from tests import mock_request, fix_matcher_rand

"""
test models.
"""

import pytest

from chatty.domain import model


@pytest.mark.usefixtures('my_init_db')
def test_state_transition(mocker, monkeypatch):
    """状態遷移のテスト"""
    fix_matcher_rand(mocker)

    from chatty.domain.user_state import (
        User,
        IdleUserState,
        SearchingUserState,
        TalkingUserState,
    )
    from chatty.domain.model.match import Language

    import requests
    mock_request(monkeypatch, requests)
    # session
    session = model.Session()

    # ユーザーの言語設定を行う
    english = (session.query(Language).get('en_US')
               or Language(id='en_US', name='English'))
    user1 = User('TEST-01')
    user1.languages = [english]
    user2 = User('TEST-02', 'TEST-02')
    user2.languages = [english]
    user3 = User('TEST-03', 'TEST-03')
    user3.languages = [english]

    session.add(user1)
    session.add(user2)
    session.commit()
    user1_c = UserContext(user1)
    user2_c = UserContext(user2)
    user3_c = UserContext(user3)
    # At first, must be NoSignUpIdle
    assert isinstance(user1_c.status, NoSignUpIdleUserState)
    user1.fb_id = "1234"
    assert isinstance(user1_c.status, IdleUserState)
    # ユーザをサーチ状態にする
    user1_c.do_search(None)
    session.commit()
    assert isinstance(user1_c.status, SearchingUserState)

    # ユーザーを会話状態にする
    user2_c.do_search(None)
    session.commit()
    assert isinstance(user1_c.status, TalkingUserState)
    assert isinstance(user2_c.status, TalkingUserState)

    # 会話を終了する
    user2_c.end_conversation_and_search(None)
    session.commit()
    assert isinstance(user1_c.status, IdleUserState)
    assert isinstance(user2_c.status, SearchingUserState)

    # not match same tuple
    user1_c.do_search(None)
    session.commit()
    assert isinstance(user1_c.status, SearchingUserState)
    assert isinstance(user2_c.status, SearchingUserState)

    # match with pother partners.
    user3_c.do_search(None)
    session.commit()
    assert isinstance(user1_c.status, SearchingUserState)
    assert isinstance(user2_c.status, TalkingUserState)
    assert isinstance(user3_c.status, TalkingUserState)

    # 会話を終了する
    user2_c.end_conversation(None)
    session.commit()
    assert isinstance(user1_c.status, SearchingUserState)
    assert isinstance(user2_c.status, IdleUserState)
    assert isinstance(user3_c.status, IdleUserState)

    user1_c.cancel_search(None)
    session.commit()
    assert isinstance(user1_c.status, IdleUserState)


@pytest.mark.usefixtures('my_init_db')
def test_user_state_check_error(mocker, monkeypatch, caplog):
    fix_matcher_rand(mocker)
    from chatty.domain.user_state import (
        User,
        IdleUserState,
        SearchingUserState,
        TalkingUserState,
    )
    from chatty.domain.model.match import Language

    import requests
    from chatty.util.fb import requests as fbreq
    mock_request(monkeypatch, requests)
    mock_request(monkeypatch, fbreq)

    # session
    session = model.Session()

    # ユーザーの言語設定を行う
    english = (session.query(Language).get('en_US')
               or Language(id='en_US', name='English'))
    user = User('TEST-01', 'TEST-01')
    user.languages = [english]
    partner = User('TEST-02', 'TEST-02')
    partner.languages = [english]

    session.add(user)
    session.add(partner)
    session.commit()
    user_c = UserContext(user)
    partner_c = UserContext(partner)
    # logging 設定
    caplog.set_level(logging.INFO)

    # エラーが返ってきた場合ワーニングログを出力
    mock_request(monkeypatch, fbreq, {
        "error": {
            "code": 190,
            "error_subcode": 1234567,
        }
    })
    user_c.status.send_message('message', action.IDLE__MESSAGE)
    # warning log が出力されているはず
    for rec in caplog.records:
        print('log: ', rec)
        if (rec.levelname == 'WARNING'
            and rec.message.startswith('Facebook send api error:')):
            break
    else:
        assert False, 'Not found error message'

    session.commit()

    # メッセージ送信先がメッセージを受信できない場合は検索，会話状態から削除する

    # 検索状態へ
    normalres = {'message_id': 'mid.1484759787552:e29cca0c16',
                 'recipient_id': '1261793003907488'}
    mock_request(monkeypatch, fbreq, normalres)
    user_c.do_search(None)
    session.commit()
    assert isinstance(user_c.status, SearchingUserState)

    mock_request(monkeypatch, fbreq, {
        "error": {
            "code": 10,
            "error_subcode": 2018108,
        }
    }, )
    user_c.status.send_message('message', action.SEARCHING__MESSAGE)
    session.commit()

    # アイドル状態になっているはず
    assert isinstance(user_c.status, IdleUserState)

    # 会話状態へ
    mock_request(monkeypatch, fbreq, normalres)
    user_c.do_search(None)
    partner_c.do_search(None)
    session.commit()

    assert isinstance(user_c.status, TalkingUserState)
    assert isinstance(partner_c.status, TalkingUserState)

    def m(url, json):
        recipient_ = json['recipient']['id']
        if recipient_ == "TEST-01":
            return MagicMock(json=MagicMock(return_value=normalres))
        elif recipient_ == "TEST-02":
            return MagicMock(json=MagicMock(return_value={
                "error": {
                    "code": 200,
                    "error_subcode": 1545041,
                }
            }
            ))
        raise ValueError(
            "dummy recipient must be TEST-01 or TEST-02 but {}".format(
                recipient_))

    monkeypatch.setattr(fbreq, 'post', m)
    user_c.status.do_message(
        MagicMock(message=MagicMock(text="hello", _fields=["text"])))
    session.commit()

    # アイドル状態になっているはず
    assert isinstance(user_c.status, IdleUserState)
    assert isinstance(partner_c.status, IdleUserState)

