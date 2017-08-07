#!/bin/bash -e
function mo(){
    python settings/msgfmt.py -o $1/LC_MESSAGES/chatty.mo $1/LC_MESSAGES/chatty.po
}
for file in chatty/locale/*; do
    echo ${file}
    mo ${file}
done