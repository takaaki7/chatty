#!/bin/bash
#$1=appid
curl "https://graph.facebook.com/v2.8/oauth/access_token?grant_type=fb_exchange_token&client_id=$1&client_secret=$2&fb_exchange_token=$3 "
