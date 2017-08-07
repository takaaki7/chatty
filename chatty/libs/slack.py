import json

import requests
from logging import getLogger

from chatty import config

logger=getLogger(__name__)

def post(text, links=[]):
    extra = ""
    for l in links:
        extra += "\n<" + l + ">"
    try:
        requests.post(
            config.SLACK_NOTIFY_URL,
            data=json.dumps({
                'text': text + extra
            }))
    except Exception as e:
        logger.error(e)