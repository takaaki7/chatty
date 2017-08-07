from mock import MagicMock
from webtest import TestApp, AppError

from chatty.domain.matcher import Matcher


def mock_request(monkeypatch, requests, dummy_res={}):
    mres = MagicMock()
    mres.json.return_value = dummy_res
    mock_post = MagicMock(return_value=mres)
    mock_get = MagicMock(return_value=mres)
    monkeypatch.setattr(requests, 'post', mock_post)
    monkeypatch.setattr(requests, 'get', mock_get)


def assert_message_is(obj, recipient, message):
    assert obj['recipient']['id'] == recipient
    assert message in obj['message']['text']


def assert_button(obj, recipient, message, buttons):
    assert obj['recipient']['id'] == recipient
    payload = obj['message']['attachment']['payload']
    assert payload['template_type'] == "button"
    assert message in payload[
        'text'], 'expect {} in pyload.text but payload is {}'.format(message,
                                                                     payload)
    pbuttons = payload['buttons']
    for i, b in enumerate(buttons):
        if b['type'] == "postback":
            assert pbuttons[i]['payload'] == b['payload']
        elif b['type'] == "web_url":
            assert b['url'] in pbuttons[i]['url']


def fix_matcher_rand(mocker):
    def ret():
        return Matcher(randomnum=0)

    mocker.patch("chatty.domain.model.match.matcher.get", ret)


class BetterTestApp(TestApp):
    """A testapp that prints the body when status does not match."""

    def _check_status(self, status, res):
        if status is not None and status != res.status_int:
            raise AppError(
                "Bad response: %s (not %s)\n%s", res.status, status, res)
        super(BetterTestApp, self)._check_status(status, res)
