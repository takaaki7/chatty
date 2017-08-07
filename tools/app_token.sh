#!/bin/bash -e
#app id and app secret
curl "https://graph.facebook.com/v2.8/oauth/access_token?client_id=$1&client_secret=$2&grant_type=client_credentials"
