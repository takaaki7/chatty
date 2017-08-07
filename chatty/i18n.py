# -*- coding:utf-8 -*-
"""Internationalization."""

from __future__ import print_function

import gettext
import logging
import threading

import os

catalogs = threading.local()


def messages_path():
    """Determine the path to the 'messages' directory as best possible."""
    module_path = os.path.abspath(__file__)
    return os.path.join(os.path.dirname(module_path), 'locale')


def gettext_getfunc(language):
    return gettext.translation('chatty', messages_path(),
                               [language], fallback=True).ugettext


def gettext_translate(s):
    try:
        return catalogs.translate(s)
    except AttributeError as e:
        logging.warning('Why has not attribute "translate".')
        logging.exception(e)

    return s
