# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import logging
import urllib2
from urlparse import urlparse

import requests

from chatty import config

if config.MOCK_FB:
    from mock import MagicMock

    requests.get = MagicMock(
        return_value=MagicMock(json=lambda: {"mocked": 1}))
    requests.post = MagicMock(
        return_value=MagicMock(json=lambda: {"mocked": 1}))
else:
    import requests
logger = logging.getLogger(__name__)
PAGE_ACCESS_TOKEN = config.FB_PAGE_ACCESS_TOKEN
FB_SEND_API = (
    'https://graph.facebook.com/v2.6/me/messages'
    '?access_token={PAGE_ACCESS_TOKEN}'
).format(PAGE_ACCESS_TOKEN=PAGE_ACCESS_TOKEN)

FB_USER_PROFILE_API_LOCALE = (
    'https://graph.facebook.com/v2.6/{user_id}'
    '?fields=locale&access_token={PAGE_ACCESS_TOKEN}'
).format(user_id='{user_id}', PAGE_ACCESS_TOKEN=PAGE_ACCESS_TOKEN)

FB_USER_PROFILE_API = (
    'https://graph.facebook.com/v2.6/{user_id}'
    '?access_token={PAGE_ACCESS_TOKEN}&fields=locale,'
    'first_name,last_name,gender'
).format(user_id='{user_id}', PAGE_ACCESS_TOKEN=PAGE_ACCESS_TOKEN)

# https://developers.facebook.com/docs/graph-api/reference/user/
FB_USER_PROFILE_API_DETAIL = (
    'https://graph.facebook.com/v2.8/{user_id}'
    '?access_token={access_token}&fields=age_range,'
    'first_name,last_name,gender,locale,location')

# https://developers.facebook.com/docs/graph-api/reference/user/picture/
PROFILE_PICTURE_API = (
    "https://graph.facebook.com/v2.9/{user_id}/picture?"
    "access_token={access_token}&redirect=0&type=square&width=300".format(
        user_id="{user_id}", access_token=PAGE_ACCESS_TOKEN)
)

# http://stackoverflow.com/questions/42279468/how-to-get-country-from-location-id-in-facebook-api
LOCATION_API = (
    "https://graph.facebook.com/v2.9/{location_id}?"
    "access_token={access_token}&fields=location"
)

_LOGIN_REDIRECT_URL = config.HEROKU_URL + \
                      "/bot/fb/signin_redirect?uid={uid}"

_PAYMENT_REDIRECT_URL = config.HEROKU_URL + \
                        "/bot/fb/buy_points?uid={uid}"

_SIGNUP_URL = ("https://www.facebook.com/v2.8/dialog/oauth?"
               "client_id={}&redirect_uri={redirect}&response_type=code&scope=user_location&state={state}"
               ).format(config.FB_APP_ID, redirect="{redirect}",
                        state="{state}")
FB_LOGIN_URL = _SIGNUP_URL.format(redirect=_LOGIN_REDIRECT_URL,
                                  state="{state}")
PAYMENT_LOGIN_URL = _SIGNUP_URL.format(redirect=_PAYMENT_REDIRECT_URL,
                                       state="{state}")
TOKEN_VERIFY_URL = ("https://graph.facebook.com/debug_token?"
                    "input_token={input_token}"
                    "&access_token={app_token}").format(
    app_token=config.FB_APP_ACCESS_TOKEN,
    input_token="{input_token}")


def login_redirect_token_check(redirect_url, code):
    # https://developers.facebook.com/docs
    # /facebook-login/manually-build-a-login-flow
    r = requests.get(
        "https://graph.facebook.com/v2.8/oauth/access_token?"
        "client_id={app_id}"
        "&redirect_uri={redirect_uri}"
        "&client_secret={app_secret}"
        "&code={code_parameter}".format(app_id=config.FB_APP_ID,
                                        redirect_uri=redirect_url,
                                        app_secret=config.FB_APP_SECRET,
                                        code_parameter=code))
    r.raise_for_status()
    token = r.json()['access_token']
    url = TOKEN_VERIFY_URL.format(input_token=token)
    r = requests.get(url)
    logger.debug("token:%s url:%s r:%s", token, url, r.json())
    r.raise_for_status()
    return r.json()['data'], token


def message(recipient, text):
    return {
        "recipient": {
            "id": recipient
        },
        "message": {
            "text": text
        }
    }


def button_data(recipient, text, buttons):
    return {
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": template_payload("button", text, buttons)
            }
        }
    }


def template_payload(type, text, buttons):
    return {
        "template_type": type,
        "text": text,
        "buttons": buttons
    }


def quick_reply_data(recipient, text, qrs):
    return {
        "recipient": {
            "id": recipient
        },
        "message": {
            "text": text,
            "quick_replies": qrs
        }
    }


def quick_reply_temp_data(recipient, temp, qrs):
    return {
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": temp
            },
            "quick_replies": qrs
        }
    }


def quick_reply(title, payload):
    return {
        "content_type": "text",
        "title": title,
        "payload": payload
    }


def generic_template(recipient, title, subtitle, imageurl):
    return {
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": title,
                            "image_url": imageurl,
                            "subtitle": subtitle,
                        }
                    ]
                }
            }
        }
    }


def generic_template_b(recipient, title, subtitle, button):
    return {
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": title,
                            "subtitle": subtitle,
                            "buttons": button,
                        }
                    ]
                }
            }
        }
    }


def generic_template_ib(recipient, title, imageurl, link, button):
    return {
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "image_aspect_ratio": "square",
                    "elements": [
                        {
                            "title": title,
                            "image_url": imageurl,
                            "default_action": {
                                "type": "web_url",
                                "url": link,
                                "messenger_extensions": True,
                                "webview_height_ratio": "tall",
                                "fallback_url": link
                            },
                            "buttons": button,
                        }
                    ]
                }
            }
        }
    }


def generic_template_itsb(recipient, title, subtitle, imageurl, buttons):
    return {
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "image_aspect_ratio": "square",
                    "elements": [
                        {
                            "title": title,
                            "subtitle": subtitle,
                            "image_url": imageurl,
                            "buttons": buttons,
                        }
                    ]
                }
            }
        }
    }


def profile_link(fbid):
    return "https://www.facebook.com/app_scoped_user_id/{id}".format(id=fbid)


def button(title, payload):
    return {
        "type": "postback",
        "title": title,
        "payload": payload
    }


def web_button(title, url, fallback_url, webview_height):
    return {"type": "web_url",
            "url": url,
            "title": title,
            "webview_height_ratio": webview_height,
            "messenger_extensions": True,
            "fallback_url": fallback_url}


def attachment(recipient, type, url):
    return {
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": type,
                "payload": {
                    "url": url
                }
            }
        }
    }


def get_locale(uid):
    url = FB_USER_PROFILE_API_LOCALE.format(user_id=uid)
    data = requests.get(url).json()
    if data:
        if 'locale' in data:
            return data.get('locale')
    return None


def send_data(data):
    return requests.post(FB_SEND_API, json=data)


def send_file(data, furl):
    filename = urlparse(furl).path.split('/')[-1]
    return requests.post(
        FB_SEND_API, data=data, files={filename: urllib2.urlopen(furl)})


def profile(uid):
    url = FB_USER_PROFILE_API.format(user_id=uid)

    return requests.get(url).json()


def profile_detail(uid, token):
    url = FB_USER_PROFILE_API_DETAIL.format(user_id=uid, access_token=token)
    return requests.get(url).json()


def profile_picture(fbid):
    url = PROFILE_PICTURE_API.format(user_id=fbid)
    return requests.get(url).json().get('data', {}).get('url', {})


def location_detail(location_id, user_access_token):
    url = LOCATION_API.format(location_id=location_id,
                              access_token=user_access_token)
    return requests.get(url).json()


def full_name(uid):
    data = profile(uid)
    first = data.get("first_name", "None")
    last = data.get("last_name", "None")
    name = data.get("name", "None")
    return "{} {} {}".format(first, last, name)
