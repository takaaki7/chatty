import pytest

from chatty import bot
from tests import mock_request


@pytest.mark.usefixtures('my_init_db')
def test_message_callback(monkeypatch):
    import requests
    mock_request(monkeypatch, requests)

    threads = bot.callback({u'entry': [{u'id': u'1878285869108664',
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
    for t in threads:
        t.join()
    args = requests.post.call_args_list
    assert len(args) == 3, "args must dashbot_in,dashbot_out but {}".format(
        args)
    assert requests.post.call_args_list[1][0][
               0] == 'https://graph.facebook.com/v2.6/me/messages?access_token=dummy', 'expect one out message but {}'.format(
        requests.post.call_args_list)
