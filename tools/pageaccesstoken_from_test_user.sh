#!/bin/bash -e
echo "pass test user page token as argument"
curl https://graph.facebook.com/v2.8/me/accounts?access_token=$1
#subscribe this to FB_APP_ACCESS_TOKEN