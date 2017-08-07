#!/bin/bash -e
python settings/pygettext.py -o chatty/locale/$1/LC_MESSAGES/chatty.po chatty/*.py
