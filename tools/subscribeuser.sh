#!/bin/bash
# $1=token got by pageaccesstoken_from_test_user.sh
curl "https://graph.facebook.com/v2.8/me/subscribed_apps?method=POST&access_token=$1"