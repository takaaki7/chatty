import logging

import redis

from chatty import config
from chatty.libs import slack

logger = logging.getLogger(__name__)


def ban_user(target):
    try:
        logger.info("banned {}".format(target))
        cli = redis.from_url(config.REDIS_URL)
        cli.incr("ban:{}".format(target), 11)
        # slack.post("[ADMIN_MESSAGE] banned {}".format(target))
    except Exception:
        logger.exception("failed to ban {} by connect redis".format(target))
        raise


def is_banned(target):
    try:
        cli = redis.from_url(config.REDIS_URL)

        cnt = cli.get("ban:{}".format(target))
        return cnt is not None and cnt > 10
    except Exception:
        logger.exception(
            "failed to check ban {} by connect redis".format(target))
        return False
