# -*- coding:utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import redis

from chatty import config
from chatty.domain import black_list

"""
test models.
"""

import pytest


@pytest.fixture()
def my_init_db():
    cli = redis.from_url(config.REDIS_URL)
    cli.flushdb()


@pytest.mark.usefixtures('my_init_db')
def test_state_transition(mocker, monkeypatch):
    assert not black_list.is_banned("1234")
    from chatty.libs import slack
    mock_send = mocker.MagicMock()
    monkeypatch.setattr(slack, "post", mock_send)
    black_list.ban_user("1234")
    assert black_list.is_banned("1234")
    assert 1 == mock_send.call_count
