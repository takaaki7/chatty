# -*- coding:utf-8 -*-
"""bot."""

from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging
import pprint as pp
from collections import namedtuple
from threading import Thread

from chatty import (
    config)
from chatty import session_scope
from chatty.domain.model import (Session, )
from chatty.domain.model.match import (
    Language,
    User,
)
from chatty.domain.user_state import UserContext
from chatty.libs import action
from chatty.libs import slack
from chatty.libs import tokener
from chatty.libs.button import (
    ACTION,
    CANCEL_SEARCH,
    END_CONVERSATION,
    SEARCH,
    START,
    SHARE_PROFILE,
    SHARE_PROFILE_PRE,
    END_CONVERSATION_AND_SEARCH
)
from chatty.util import fb
from chatty.util.actionlogger import actionlogger
from chatty.util.fb import button as b

logger = logging.getLogger(__name__)

VALIDATION_TOKEN = config.FB_VALIDATION_TOKEN


def convert(dictionary):
    nd = {}
    for key, value in dictionary.items():
        if isinstance(value, dict):
            nd[key] = convert(value)
        elif isinstance(value, list):
            nd[key] = [convert(i) for i in value]
        else:
            nd[key] = value
    return namedtuple('CallbackData', nd.keys())(**nd)


def verify_token(token):
    return token == VALIDATION_TOKEN


@session_scope
def callback(data_):
    actionlogger.emit_incoming(data_)
    logger.debug('Recived callback: %s', pp.pformat(data_))
    data = convert(data_)
    threads = []
    if data.object == 'page':

        # Iterate over each entry
        # There may be multiple if batched
        for entry in data.entry:

            for message in entry.messaging:
                if config.UNDER_MAINTENANCE:
                    t = Thread(target=receive_under_maintenance,
                               args=(message,))
                    t.start()
                elif 'message' in message._fields:
                    if 'quick_reply' in message.message._fields:
                        t = Thread(target=received_quick_reply,
                                   args=(message,))
                        t.start()
                    else:
                        t = Thread(target=received_message, args=(message,))
                        t.start()
                    threads.append(t)
                elif 'postback' in message._fields:
                    t = Thread(target=received_postback, args=(message,))
                    t.start()
                    threads.append(t)
                else:
                    logger.warning("Webhook received unknown message: %s",
                                   message)
    return threads


def receive_under_maintenance(message):
    fb.send_data(
        fb.message(message.sender.id,
                   "Sorry for inconvenience, Chatty is under maintenance. We'll be back soon."))


@session_scope
def received_message(message):
    user_id = message.sender.id
    user_c = UserContext.get(user_id)
    if "text" in message.message._fields:
        t = message.message.text
        if t == "system-reset-lastmatched":
            reset_last_matched(user_id)
            return
        if t == "system-reset-fb-id":
            reset_fb_id(user_id)
            return
        if t == "system-index-page":
            send_index_page_test(user_c)
            return
        if t == "system-login-page":
            send_login_page(user_c)
            return
        if t == "system-buy-button-page":
            send_purchase_button_page(user_c)
            return
        if t == "system-reset-gender":
            reset_gender(user_id)
            return
    user_c.do_message(message)


@session_scope
def received_quick_reply(message):
    payload = message.message.quick_reply.payload
    run_methods(message, payload)


@session_scope
def received_postback(message):
    payload = message.postback.payload
    run_methods(message, payload)


def run_methods(message, payload):
    user_id = message.sender.id
    user_c = UserContext.get(user_id)
    if payload.startswith("PREREPORT-"):
        prereport_user(user_c, payload.split("-")[1])
        return
    if payload.startswith("REPORT-"):
        report_user(user_c, payload.split("-")[1])
        return
    {
        ACTION: user_c.do_action,
        SEARCH: user_c.do_search,
        START: user_c.do_start,
        CANCEL_SEARCH: user_c.cancel_search,
        END_CONVERSATION: user_c.end_conversation,
        END_CONVERSATION_AND_SEARCH: user_c.end_conversation_and_search,
        SHARE_PROFILE: user_c.share_profile,
        SHARE_PROFILE_PRE: user_c.share_profile_pre,
    }.get(payload, user_c.do_unknown)(message)


@session_scope
def do_action(uid):
    if not User.exists(uid):
        return
    UserContext.get(uid).do_action({})


@session_scope
def translate(uid, text):
    return UserContext.get(uid)._(text)


def prereport_user(user_c, target):
    user_c.send_btn(
        user_c._(
            "If the person you chatted with was a malicious user,"
            " you can report them via the [Report] button."),
        [b(user_c._("Report"), "REPORT-{}".format(target))],
        action.PREREPORTED_USER)


def report_user(user_c, target):
    tok = tokener.gen_token_invert(target, tokener.NS_BAN_USER)
    slack.post(
        "Ban name:{} id:{} (from {} {}?"
        " https://www.facebook.com/{}/messages \n"
        "{}".format(
            fb.full_name(target), target, fb.full_name(user_c.user.id),
            user_c.user.id, config.BOT_NAME,
            config.HEROKU_URL + "/ban_user/" + tok
        )
        # not send full link to avoid miss ban. add /confirm to foot manually.
    )
    user_c.send_message(user_c._("Reported."), action.REPORTED_USER)


def reset_last_matched(user_id):
    user = User.get(user_id)
    user.last_matched = None


def reset_fb_id(user_id):
    user = User.get(user_id)
    user.fb_id = None


def reset_gender(user_id):
    user = User.get(user_id)
    user.gender = None
    user.locale = None
    user.country = None
    user.fb_id = None


def send_index_page_test(user_c):
    user_c.send_btn("index", [fb.web_button("index", "https://www.chatty.top",
                                            "https://www.chatty.top", "full")],
                    "test-index")


def send_login_page(user_c):
    user_c.send_btn("You need to sign up with facebook.",
                    [fb.web_button(
                        "Sign up",
                        fb.FB_LOGIN_URL.format(user_id=user_c.user.id),
                        fb.FB_LOGIN_URL.format(user_id=user_c.user.id),
                        "full")], "test-login-page")


def send_purchase_button_page(user_c):
    user_c.send_btn("you need to buy points",
                    [user_c.purchase_points_button()], "test-buy-page")


@session_scope
def get_settings(user_id):
    user = User.get(user_id)
    if user:
        return dict(
            languages=list([lang.id for lang in user.languages]),
            finding_genders=user.finding_genders.split(","),
            location_enabled=user.location_enabled,
            country=user.country or "undefined",
            current_latitude=user.current_latitude,
            current_longitude=user.current_longitude,
            search_radius=user.search_radius or 500,
        )
    return dict(languages=[],
                finding_genders=["male", "female"],
                location_enabled=False,
                country="undefined",
                current_latitude=None,
                current_longitude=None,
                search_radius=500
                )


@session_scope
def set_settings(user_id, languages, finding_genders,
                 current_latitude,
                 current_longitude,
                 search_radius, location_enabled):
    user_c = UserContext.get(user_id)
    user = user_c.user
    user.languages = [Language.get(lang) for lang in languages]
    user.finding_genders = ",".join(finding_genders)
    user.current_latitude = current_latitude
    user.current_longitude = current_longitude
    user.search_radius = search_radius
    user.location_enabled = location_enabled
    user_c.send_message(user_c._("Changes saved."), action.CHANGED_LANGUAGE)


@session_scope
def get_language():
    return [(lang.id, lang.name) for lang in Language.all()]


@session_scope
def logged_in_with_fb(uid, code, redirect_url):
    fb_user_id, token, user = _login_update(code, uid, redirect_url)
    user.signup_date = datetime.datetime.now()
    if user.fb_id is None:
        user.fb_id = fb_user_id
        user.fb_access_token = token
        uc = UserContext.get(uid)
        uc.send_message(uc._(
            "Sign up completed! "
            "Click the Settings button to set discovery settings."),
            action.IDLE__SIGN_UP_COMPLETED)
        uc.do_action({}, action.IDLE__ACTION_AFTER_SIGNUP)


@session_scope
def login_update(code, uid, redirect_url):
    fb_user_id, _, _ = _login_update(code, uid, redirect_url)
    return fb_user_id


def _login_update(code, uid, redirect_url):
    data, token = fb.login_redirect_token_check(redirect_url, code)
    if data['app_id'] != config.FB_APP_ID:
        raise ValueError('app id is incorrect.')
    session = Session()
    user = session.query(User).get(uid)
    if user is None:
        raise ValueError('User with page id {} must already exist'.format(uid))
    fb_user_id = data['user_id']
    profile = fb.profile_detail(fb_user_id, token)
    logger.debug("logged in: %s", profile)
    if 'age_range' in profile:
        user.age_min = profile['age_range'].get('min', None)
        user.age_max = profile['age_range'].get('max', None)
    if 'location' in profile and 'id' in profile['location']:
        locdetail = fb.location_detail(profile['location']['id'], token).get(
            'location', None)
        user.country = locdetail.get('country', None)
        user.state = locdetail.get('state', None)
        user.city = locdetail.get('city', None)
    return fb_user_id, token, user
