import base64
from logging import getLogger

import M2Crypto

from chatty.util import cache

NS_PAYMENT = "payment_access_token"
NS_PAYMENT_SECOND = "payment_second_access_token"
NS_LOGIN = "login_access_token"
NS_BAN_USER = "ban_user_token"
logger = getLogger(__name__)


# https://stackoverflow.com/questions/817882/unique-session-id-in-python/6092448#6092448
def gen_token(key, namespace, ttl_seconds=60 * 30):
    token = gen_random()
    cache.cacher.set(key, token, ttl_seconds, namespace)
    return token


def gen_random():
    return base64.urlsafe_b64encode(M2Crypto.m2.rand_bytes(16)).replace("=",
                                                                        "_")


def check(key, token, namespace, delete=True):
    tok = cache.cacher.get(key, namespace)
    if tok and tok == token:
        if delete:
            cache.cacher.delete_one(key, namespace)
        return True
    else:
        logger.info(
            'found token {} for key {} ns {}, but given:{}'.format(tok, key,
                                                                   namespace,
                                                                   token))
        return False


def gen_token_invert(value, namespace, ttl_seconds=60 * 30):
    token = gen_random()
    # 10minutes
    cache.cacher.set(token, value, ttl_seconds, namespace)
    return token


def get_value_invert(token, namespace):
    return cache.cacher.get(token, namespace)
