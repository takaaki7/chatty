# -*- coding:utf-8 -*-
"""chatty server."""

from __future__ import print_function
from __future__ import unicode_literals

import hashlib
import hmac
import logging
from threading import Thread

import bottle
import requests
from bottle import (
    abort,
    error,
    get,
    hook,
    post,
    request,
    response,
    route,
    run,
    static_file,
    url,
)

import bot
import config

logger = logging.getLogger(__name__)


@route('/p/<filepath:path>')
@route('/public/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='static')


@get('/bot/fb/callback')
def verify_token():
    req = bottle.request
    token = req.query['hub.verify_token']

    if bot.verify_token(token):
        return req.query.get('hub.challenge', '')

    logger.warning('Error, wrong validation token: %s', token)
    abort(403, 'Error, wrong validation token')


@post('/bot/fb/callback', name='callback')
def callback():
    try:
        data = request.json
        t = Thread(target=bot.callback, args=(data,))
        t.start()

    except Exception as err:
        logger.exception('Error dosomething: %s', err)

    finally:
        response.status = 200


@hook('before_request')
def verify_request_signature():
    if config.DEVELOP:
        return
    if request.path != url('callback') or request.method == 'GET':
        return

    signature = request.get_header('x-hub-signature')

    if not signature:
        logger.error("Couldn't validate the request signature.")
        abort(403, "Couldn't validate the request signature.")

    elements = signature.split('=')
    sig_hash = elements[1]

    expected_hash = hmac.new(
        config.FB_APP_SECRET,
        request.body.read(),
        hashlib.sha1).hexdigest()

    if sig_hash != expected_hash:
        logger.info(sig_hash)
        logger.info(expected_hash)
        logger.error("Couldn't validate the request signature.")
        abort(403, "Couldn't validate the request signature.")


@error(500)
def error_handler_500(err):
    exception = err.exception
    if type(exception) == requests.exceptions.HTTPError:
        logger.error(
            "http error url:{} res:{}".format(exception.request.url,
                                              exception.response.text))
    return "Something went wrong. Please contact us by https://m.me/ChattySupport"


from apis import apis
from views import views

app = bottle.default_app()
app.merge(apis)
app.merge(views)

if __name__ == "__main__":
    run(app=app, host='0.0.0.0', port=8080)
