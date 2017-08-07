# -*- coding:utf-8 -*-
"""configure."""

from __future__ import print_function
from __future__ import unicode_literals

import os

DEVELOP = os.environ.get('DEVELOP')
DEBUG = os.environ.get('DEBUG') == "TRUE"
MOCK_FB = os.environ.get('MOCK_FB') == "TRUE"

"""Facebook関連."""
# VALIDATION_TOKEN
# [https://developers.facebook.com/apps/1106820979436485/webhooks/]
FB_VALIDATION_TOKEN = os.environ['FB_VALIDATION_TOKEN']

# https://developers.facebook.com/docs/facebook-login/access-tokens/#apptokens
FB_APP_ACCESS_TOKEN = os.environ['FB_APP_ACCESS_TOKEN']

# PAGE_ACCESS_TOKEN
# [https://developers.facebook.com/docs/messenger-platform/send-api-reference]
FB_PAGE_ACCESS_TOKEN = os.environ['FB_PAGE_ACCESS_TOKEN']

FB_APP_ID = os.environ['FB_APP_ID']

FB_APP_SECRET = os.environ['FB_APP_SECRET']

"""Dashbot"""
DASHBOT_API_KEY = os.environ['DASHBOT_API_KEY']

"""Postgress."""
DATABASE_URL = os.environ['DATABASE_URL']

"""Heroku."""
HEROKU_URL = os.environ['HEROKU_URL']

ENABLED_LANGUAGES = ["en_US", "vi_VN", "ar_AR", 'fr_FR', "id_ID"]

REDIS_URL = os.environ['REDIS_URL']

BOT_NAME = os.environ['BOT_NAME']

ADMIN_USERS = os.environ['ADMIN_USERS'].split(":")

STRIPE_SECRET_KEY = os.environ['STRIPE_SECRET_API_KEY']

STRIPE_PUBLISHABLE_KEY = os.environ['STRIPE_PUBLISH_API_KEY']

UNDER_MAINTENANCE = os.environ.get('UNDER_MAINTENANCE',"false")=="TRUE"

SLACK_NOTIFY_URL=os.environ['SLACK_NOTIFY_URL']

CRYPTO_SECRET_KEY=os.environ['CRYPTO_SECRET_KEY']

