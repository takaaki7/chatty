# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import functools
import logging
import pprint as pp

from sqlalchemy.exc import IntegrityError

from chatty import config, i18n
from chatty.domain import black_list
from chatty.domain.model import Session
from chatty.domain.model.match import Match, MatchingQueue, User, MatchHistory
from chatty.libs import action, tokener, uidcrypt
from chatty.libs.button import (
    CANCEL_SEARCH,
    END_CONVERSATION,
    END_CONVERSATION_AND_SEARCH,
    SEARCH,
    SHARE_PROFILE,
    SHARE_PROFILE_PRE,
)
from chatty.util import fb
from chatty.util.actionlogger import actionlogger
from chatty.util.fb import button as b

logger = logging.getLogger(__name__)


def check_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        has_error = kwargs.get('has_error')
        response = func(*args, **kwargs)
        r = response.json()
        logging.debug('response: %s', pp.pformat(r))

        if 'error' not in r:
            return

        logging.warning('Facebook send api error: %s', pp.pformat(r))
        user_status = args[0]
        user = user_status.user

        # 2018065: over 24hours
        # 2018108 ,1545041: User blocked or left and we can't send message.
        if r['error'].get('error_subcode') in (2018108, 1545041, 2018065):
            MatchingQueue.remove(user)
            if user.partner:
                pc = UserContext(user.partner)
                pc.send_btn(
                    pc._("Stranger has disconnected."),
                    [pc.new_chat(), pc.langb()],
                    action.TALKING__ERROR_AND_DISCONNECTED)
                user.partner.partner = None
                user_status.delegate.on_match_ended(user_status, pc)

                # don't send message if this is called by error
        elif not has_error:
            user_status.send_message(
                user_status._('Sending failed. Try it again later.'),
                action.FB_ERROR_RETURNED, has_error=True)

    return wrapper


class UserStateDelegate(object):
    def on_found_partner(self, userstate, partnerstate, record):
        user = userstate.user
        partner = partnerstate.user

        def consumepoint_if_should(u, finding_genders):
            if finding_genders == "female" and u.gender == "male":
                u.points -= 10
                return 10
            return 0

        fp = consumepoint_if_should(user, user.finding_genders)
        wp = consumepoint_if_should(partner, record.finding_genders)

        Match.create(user.id, partner.id, record.created_at, fp, wp)

    def on_speak(self, userstate):
        pass

    def on_try_search(self, us):

        if black_list.is_banned(us.user.id):
            us.send_message(
                us._(
                    "Your Chatty account has been suspended"
                    " due to malicious activity."
                    "If you think this account was suspended incorrectly,"
                    " please contact https://m.me/ChattySupport"),
                action.YOU_ARE_BANNED)
            return False

        if us.user.gender == "male" and us.user.finding_genders == "female":
           if us.user.points < 10:
               buttons = [us.purchase_points_button()]
               us.send_btn(us._(
                   "Not enough points, please purchase more.\n"
                   "Selecting a gender preference require points.(10 points per use)"),
                   buttons,
                   action.IDLE__POINT_NEEDED)
               return False
        return True

    def on_match_ended(self, userstate, partnerstate):
        Match.find_and_end(userstate.user.id)
        # MatchHistory.create(match, userstate.user.id)


class UserContext(object):
    def __init__(self, user):
        self.user = user

    @classmethod
    def get(cls, user_id):
        return UserContext(User.get(user_id))

    @property
    def status(self):
        if self.user.partner:
            return TalkingUserState(self.user)
        elif self.user.matching_queue_item:
            return SearchingUserState(self.user)
        elif self.user.fb_id is None:
            return NoSignUpIdleUserState(self.user)
        else:
            return IdleUserState(self.user)

    def __getattr__(self, name):
        """処理をステータスオブジェクトに委譲する"""
        return getattr(self.status, name)


class UserState(object):
    def __init__(self, user):
        self.user = user
        self.delegate = UserStateDelegate()

    def _(self, s):
        return i18n.gettext_getfunc(self.user.locale)(s)

    @check_error
    def send_action(self, data, event, has_error=False):
        r = fb.send_data(data)
        actionlogger.emit_outgoing(data, r.json(), event)
        return r

    @check_error
    def send_file(self, data, url, event, has_error=False):
        r = fb.send_file(data, url)
        actionlogger.emit_outgoing(data, r.json(), event)
        return r

    def send_message(self, txt, event, has_error=False):
        data = fb.message(self.user.id, txt)
        logging.debug('send message: %s', pp.pformat(data))
        self.send_action(data, event, has_error=has_error)

    def send_btn(self, text, buttons, event, user_id=None):
        self.send_action(
            fb.button_data(user_id or self.user.id, text, buttons), event)

    def send_attachment(self, attach, recipient):
        # disable image and video temporary to avoid explicit contents.
        # if attach.type in ['image', 'audio', 'video']:
        if attach.type in ['audio']:
            self.send_action(
                fb.attachment(recipient, attach.type, attach.payload.url),
                action.TALKING__ATTACHMENT_PASSIVE)
        elif attach.type == 'file':
            self.send_file({
                'recipient': '{"id": "%s"}' % recipient,
                "message": '{"attachment": {"type": "file", "payload": {}}}'
            }, attach.payload.url, action.TALKING__ATTACHMENT_PASSIVE)
        else:
            self.send_message(self._('This message type is not supported.'),
                              action.TALKING__ERROR_UNSUPPORTED_MESSAGE)

    def langb(self):
        uid = uidcrypt.encryptuid(self.user.id)
        url = "{url}/{uid}/settings".format(url=config.HEROKU_URL, uid=uid)
        return fb.web_button(self._("Discovery Settings"), url, url, "tall")

    def purchase_points_button(self):
        url = fb.PAYMENT_LOGIN_URL.format(
            state=tokener.gen_token(self.user.id,
                                    tokener.NS_PAYMENT),
            uid=uidcrypt.encryptuid(self.user.id))
        return fb.web_button(self._("Purchase Points"), url, url, "full")

    def new_chat(self):
        return b(self._("New Chat"), SEARCH)

    def do_activated(self):
        self.send_btn(self._("Now you can start a new chat!"),
                      [self.new_chat(), self.langb()], action.IDLE__ACTIVATED)

    def do_unknown(self, message):
        logging.warning('received unknown payload: %s',
                        message)
        self.do_action(message)

    def do_start(self, message):
        self.do_unknown(message)

    def do_action(self, message):
        self.do_unknown(message)

    def do_search(self, message):
        self.do_unknown(message)

    def do_message(self, message):
        self.do_unknown(message)

    def share_profile_pre(self, message):
        self.do_unknown(message)

    def share_profile(self, message):
        self.do_unknown(message)

    def cancel_search(self, message):
        self.do_unknown(message)

    def end_conversation(self, message, partner_active=True):
        self.do_unknown(message)

    def end_conversation_and_search(self, message):
        self.do_unknown(message)

    def _do_search(self, message):

        if not self.delegate.on_try_search(self):
            return

        partner = MatchingQueue.match_partner(self.user)
        if partner:
            self.match_user(partner, message)
            return

        MatchingQueue.push(self.user)

        self.send_message(self._(
            "Finding someone you can chat with..."
        ), action.IDLE__ACTION_SEARCH_WAITING)

    def match_user(self, partner, message):
        logging.debug('match user %s and %s', self.user.id, partner.id)

        session = Session()
        try:
            pc = UserContext(partner)
            self.user.partner = partner
            partner.partner = self.user
            self.user.last_matched = partner.id
            partner.last_matched = self.user.id
            record = MatchingQueue.remove(partner)
            # パートナーと関連が可能かを確認するためにコミットする
            session.commit()
            self.delegate.on_found_partner(self, pc, record)
            title = "You're now chatting with someone new!\n"
            subtitle = "Choose 'Menu' from the menu '≡'" \
                       " in the corner or tap the button bellow" \
                       " to terminate your conversation."

            def send_matched(userc1, userc2, event):
                if userc1.user.version >= "2.0" and userc2.user.version >= "2.0":
                    return userc1.send_action(fb.generic_template_itsb(
                        userc1.user.id, userc1._(title), userc1._(subtitle),
                        fb.profile_picture(userc2.user.fb_id),
                        [b(userc1._("End Chat"), END_CONVERSATION),
                         b(userc1._("Share Your Profile"),
                           SHARE_PROFILE_PRE)]), event)
                else:
                    return userc1.send_action(
                        fb.generic_template_b(
                            userc1.user.id, userc1._(title),
                            userc1._(subtitle), [
                                b(userc1._("End Chat"), END_CONVERSATION),
                                b(userc1._("Share Your Profile"),
                                  SHARE_PROFILE_PRE)]), event)

            send_matched(pc, self, action.IDLE__ACTION_SEARCH_FOUND_PASSIVE)

            # if partner block us, we handle error occured above and user.partner is deleted.
            if self.user.partner:
                send_matched(self, pc, action.IDLE__ACTION_SEARCH_FOUND)
            else:
                self.do_search(message)


        except IntegrityError as e:
            session.rollback()
            logging.exception(e)
            self.do_search(message)


class NoSignUpIdleUserState(UserState):
    def do_start(self, message):
        self.send_action(
            fb.generic_template(
                self.user.id,
                self._("Welcome to Chatty!"),
                self._(
                    "Chatty lets you chat"
                    " and have fun with new people right now."),
                config.HEROKU_URL + "/p/images/toplogowelcome.png"),
            action.NO_SIGN_UP_IDLE_WELCOME)
        self.do_action(message, action.NO_SIGN_UP_IDLE_WELCOME_2)

    def do_action(self, message, event=action.NO_SIGN_UP_IDLE_ACTION):
        uidc = uidcrypt.encryptuid(self.user.id)
        url = fb.FB_LOGIN_URL.format(
            state=tokener.gen_token(self.user.id, tokener.NS_LOGIN),
            uid=uidc)
        buttons = [
            fb.web_button(self._("LOG IN WITH FACEBOOK"), url, url, "compact")]
        self.send_btn(
            self._(
                "Please sign in with Facebook. We don't post anything to Facebook."
            ),
            buttons, event)
        self.user.version = "2.0"


class IdleUserState(UserState):
    def do_message(self, message):
        self.send_btn(
            self._(
                "Do you want to start a new chat?\n"
                "Each other's profile picture will be shared when matched with someone new."
            ), [self.new_chat(), self.langb()], action.IDLE__MESSAGE)
        self.user.version = "2.0"

    def do_action(self, message, event=action.IDLE__ACTION):
        self.send_btn(
            self._("Do you want to start a new chat?\n"
                   "Each other's profile picture will be shared when matched with someone new."),
            [self.new_chat(), self.langb()], event)
        self.user.version = "2.0"

    def do_search(self, message):
        self._do_search(message)


class SearchingUserState(UserState):
    def do_message(self, message):
        self.send_btn(
            self._("Finding someone new...\n"
                   "Want to interrupt searching?"),
            [b(self._("Interrupt searching"), CANCEL_SEARCH)],
            action.SEARCHING__MESSAGE)

    def do_action(self, message):
        self.send_btn(
            self._("Finding someone new...\n"
                   "Want to interrupt searching?"),
            [b(self._("Interrupt searching"), CANCEL_SEARCH)],
            action.SEARCHING__ACTION)

    def cancel_search(self, message):
        MatchingQueue.remove(self.user)

        self.send_btn(
            self._("Searching interrupted."),
            [self.langb(), self.new_chat()], action.SEARCHING__ACTION_CANCEL)


class TalkingUserState(UserState):
    def do_message(self, message):
        partner = self.user.partner
        partner_id = partner.id

        if 'text' in message.message._fields:
            message_text = message.message.text
            pc = UserContext(partner)
            pc.send_action(
                fb.quick_reply_data(partner_id, message_text, [
                    fb.quick_reply(pc._("Share Your Profile"),
                                   SHARE_PROFILE_PRE)]),
                action.TALKING__MESSAGE_PASSIVE)
            self.delegate.on_speak(self)
        elif 'attachments' in message.message._fields:
            for attach in message.message.attachments:
                self.send_attachment(attach, partner_id)
        else:
            logging.info('no supported message: %s', pp.pformat(message))
            self.send_message(self._('This message type is not supported.'),
                              action.TALKING__ERROR_UNSUPPORTED_MESSAGE)

    def do_action(self, message):
        self.send_btn(
            self._("End Chat?"),
            [b(self._("End"), END_CONVERSATION),
             b(self._("New Chat"), END_CONVERSATION_AND_SEARCH),
             b(self._("Share Your Profile"), SHARE_PROFILE_PRE)],
            action.TALKING__ACTION)

    def do_search(self, message):
        self.end_conversation_and_search(message)

    def share_profile_pre(self, message):
        self.send_btn(self._(
            "Send a link to your Facebook profile?"
        ), [b(self._("Send"), SHARE_PROFILE)],
            action.TALKING__SHARE_PROFILE_PRE)

    def share_profile(self, message):
        pc = UserContext(self.user.partner)
        link = fb.profile_link(self.user.fb_id)
        pc.send_action(
            fb.generic_template_ib(
                pc.user.id,
                pc._("Profile shared."),
                fb.profile_picture(self.user.fb_id),
                link,
                [
                    fb.web_button(pc._("View Profile"), link, link, "tall"),
                    b(pc._("Share Your Profile"), SHARE_PROFILE_PRE)
                ],
            ), action.TALKING__SHARED_PROFILE_PASSIVE)
        self.send_message(self._("Shared."),
                          action.TALKING__SHARED_YOUR_PROFILE)

    def end_conversation(self, message, partner_active=True,
                         event=action.TALKING__END_CHAT, with_btn=True):
        me = self.user
        partner = self.user.partner
        partner_c = UserContext(partner)
        pid = partner.id
        me.partner = None
        self.delegate.on_match_ended(self, partner_c)
        if with_btn:
            if self.user.version < "2.0":
                text = self._("Chat ended.") + "\n" + self._(
                    "Do you want to start a new chat?\n"
                    "Each other's profile picture will be shared when matched with someone new."
                )
                self.user.version = "2.0"
            else:
                text = self._("Chat ended.")
            self.send_btn(text, [self.new_chat(), self.langb(),
                                 b(self._("Report"),
                                   "PREREPORT-{}".format(pid))], event)
        else:
            self.send_message(self._("Chat ended."), event)

        if partner and partner_active:
            if partner.version < "2.0":
                text = partner_c._(
                    "Stranger has disconnected.") + "\n" + partner_c._(
                    "Do you want to start a new chat?\n"
                    "Each other's profile picture will be shared when matched with someone new."
                )
                partner.version = "2.0"
            else:
                text = partner_c._("Stranger has disconnected.")
            partner_c.send_btn(
                text, [partner_c.new_chat(), partner_c.langb(),
                       b(partner_c._("Report"), "PREREPORT-{}".format(me.id))],
                action.TALKING__END_CHAT_PASSIVE)

    def end_conversation_and_search(self, message):
        self.end_conversation(message,
                              event=action.TALKING__END_CHAT_AND_NEW_CHAT,
                              with_btn=False)
        self._do_search(message)
