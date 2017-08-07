# -*- coding: utf-8 -*-

import logging
import threading

import redis
from werkzeug.local import LocalProxy

from chatty import config

tls = threading.local()
logger = logging.getLogger(__name__)


class RedisCacher(object):
    def __init__(self):
        self._con = redis.from_url(config.REDIS_URL)

    def get(self, key, namespace=None):
        if namespace:
            key = "{}.{}".format(namespace, key)
        try:
            return self._con.get(key)
        except redis.exceptions.ConnectionError:
            pass

    def set(self, key, val, time=None, namespace=None):
        if namespace:
            key = "{}.{}".format(namespace, key)
        try:
            if time:
                return self._con.setex(key, val, time)
            else:
                return self._con.set(key, val)
        except redis.exceptions.ConnectionError:
            pass

    def delete(self, *args):
        return self._con.delete(*args)

    def delete_one(self, key, namespace):
        return self._con.delete("{}.{}".format(namespace, key))

    def flushdb(self, *args):
        return self._con.flushdb(*args)


def get_cacher(cacher=RedisCacher):
    if hasattr(tls, '_cacher'):
        return tls._cacher
    tls._cacher = cacher()
    return tls._cacher


cacher = LocalProxy(get_cacher)
