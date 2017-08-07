# -*- coding:utf-8 -*-
"""chatty server."""
from __future__ import print_function
from __future__ import unicode_literals

import json
import logging

from bottle import Bottle, response, HTTPError
from bottle import (
    abort,
    request,
)

import bot
from chatty.domain import black_list
from chatty.domain import payment
from chatty.domain.model.match import User
from chatty.libs import uidcrypt, tokener

logger = logging.getLogger(__name__)
apis = Bottle()

@apis.post('/<uidenc>/log', name='log')
def log(uidenc):
    uid = uidcrypt.decryptuid(uidenc)
    json = request.json
    json['uid'] = uid
    try:
        json['locale'] = User.get(uid).locale
    except Exception:
        logger.exception("faild to get ui lang ")
    logger.info("kpi_action:{}".format(json))


@apis.post('/<uidenc>/settings', name='post_settings')
def post_settings(uidenc):
    uid = uidcrypt.decryptuid(uidenc)
    logger.debug("%s", request.forms.items())
    languages = request.forms.getall('languages')
    genders = request.forms.getall('genders')
    l = len(genders)
    assert l <= 2
    if l == 0 or l == 2:
        g = ["male", "female"]
    else:
        assert genders[0] in ["male", "female"]
        g = [genders[0]]
    lat = request.forms.get('latitude', default=None, type=float)
    lon = request.forms.get('longitude', default=None, type=float)
    sr = request.forms.get('search_radius', default=None, type=int)
    le = request.forms.get('location_enabled', None) == "true"

    bot.set_settings(uid, languages, g, lat, lon, sr, le)
    return "OK"


@apis.get('/ban_user/<token>/confirm', name='ban')
def post_ban_user(token):
    uid = tokener.get_value_invert(token, tokener.NS_BAN_USER)
    black_list.ban_user(uid)
    return "OK"
