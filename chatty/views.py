# -*- coding:utf-8 -*-
"""chatty server."""

from __future__ import print_function
from __future__ import unicode_literals

import logging

import config
import requests
from bottle import Bottle, view, abort, HTTPError, redirect
from bottle import (
    request,
    url,
)

import bot
from chatty.domain.model.match import User
from chatty.domain.model.points import MenuPrice
from chatty.domain.user_state import UserContext
from chatty.libs import uidcrypt, tokener
from chatty.util import fb

logger = logging.getLogger(__name__)
views = Bottle()


@views.get('/')
@view("index")
def index():
    return dict()


def check_maintenance(func):
    import functools
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if config.UNDER_MAINTENANCE:
            abort(503,
                  "Sorry for inconvenience, Chatty is under maintenance. We'll be back soon.")

        return func(*args, **kwargs)

    return wrapper


@views.get('/bot/fb/signin_redirect')
@view('signin_completed')
@check_maintenance
def login_redirect():
    uid = None
    token_ = None
    try:
        token_ = request.query.get('state')
        uidenc = request.query.get('uid')
        uid = uidcrypt.decryptuid(uidenc)
        tok_valid = tokener.check(uid, token_, tokener.NS_LOGIN)
        if not tok_valid:
            abort(400, "Something went wrong. Token might be expired")
        bot.logged_in_with_fb(uid, request.query.get("code"),
                              fb._LOGIN_REDIRECT_URL.format(uid=uidenc))
    except HTTPError as e:
        logger.exception(
            "failed to login for uid:{} token:{}".format(uid, token_))
        bot.do_action(uid)
        raise e
    except requests.exceptions.HTTPError as e:
        logger.exception("Failed {}".format(e.response.text))
    except Exception as e:
        bot.do_action(uid)
        logger.exception(
            "Failed to login with bad access.state:{} uid: {} token:{}".format(
                request.query.get('state'), uid, token_))
        abort(400, "Something went wrong. Please try it again. If the problem persists, please contact us at https://m.me/ChattySupport")
        return
    return dict()


from forex_python.converter import CurrencyCodes

currency_codes = CurrencyCodes()

DISPUTE_LABELS = {"500p": "", "1500p": "SAVE 20%!",
                  "3000p": "SAVE 50%!"}


class Menu(object):
    def __init__(self, menu):
        self.points = menu.points
        self.price = menu.price
        self.currency = menu.currency
        self.dispute_label = DISPUTE_LABELS[str(menu.points) + "p"]


class Lang(object):
    def __init__(self, code, name, checked):
        self.code = code
        self.name = name
        self.checked = checked


@views.get('/<uidenc>/settings', name='settings')
@view('settings', url=url)
@check_maintenance
def settings(uidenc):
    uid = uidcrypt.decryptuid(uidenc)
    settings = bot.get_settings(uid)
    languages = [Lang(code=k, name=v, checked=(k in settings['languages']))
                 for k, v in
                 filter(lambda (k1, v1): k1 in config.ENABLED_LANGUAGES,
                        bot.get_language())]
    languages.sort(key=lambda x: x.name)
    userc = UserContext.get(uid)
    return dict(settings=settings,
                languages=languages,
                buy_points_url=fb.PAYMENT_LOGIN_URL.format(
                    uid=uidenc,
                    state=tokener.gen_token(uid, tokener.NS_PAYMENT)),
                userc=userc)


@views.get('/<uidenc>/set_lang_complete', name='set_lang_complete')
@view('set_lang_complete', url=url)
@check_maintenance
def set_lang_complete(uidenc):
    uid = uidcrypt.decryptuid(uidenc)
    user_languages, _ = bot.get_settings(uid)
    languages = [Lang(code=k, name=v, checked=(k in user_languages))
                 for k, v in bot.get_language() if k in user_languages]
    return dict(uidenc=uidenc, languages=languages)
