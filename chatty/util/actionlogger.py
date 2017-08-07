import logging
from threading import Thread

import requests
from werkzeug.local import LocalProxy

import chatty.config

logger = logging.getLogger(__name__)

INCOMING = "https://tracker.dashbot.io/track?" \
           "platform=facebook&v=0.8.2-rest&" \
           "type=incoming&apiKey={}".format(chatty.config.DASHBOT_API_KEY)
OUTGOING = "https://tracker.dashbot.io/track?" \
           "platform=facebook&v=0.8.2-rest&" \
           "type=outgoing&apiKey={}".format(chatty.config.DASHBOT_API_KEY)


class ActionLogger(object):
    def emit_incoming(self, json):
        t = Thread(target=_emit, args=(INCOMING, json))
        t.start()

    def emit_outgoing(self, json, resbody, templateId):
        json['dashbotTemplateId'] = templateId
        j = {
            "qs": {
                "access_token": chatty.config.FB_PAGE_ACCESS_TOKEN
            },
            "uri": "https://graph.facebook.com/v2.6/me/messages",
            "json": json,
            "method": "POST",
            "responseBody": resbody
        }
        t = Thread(target=_emit, args=(OUTGOING, j))
        t.start()


def _emit(url, dict_object):
    try:
        r = requests.post(url, json=dict_object, timeout=3)
        r.raise_for_status()
    except Exception as e:
        # ignore exception as default
        logger.exception(
            "req:{} body:{} error:{}".format(url, dict_object, e))


actionlogger = LocalProxy(ActionLogger)
