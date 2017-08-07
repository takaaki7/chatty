#!/bin/bash

expect -c "
set timeout 8
spawn /usr/local/bin/heroku redis:cli --remote staging --confirm chatty-bot-staging
expect \">\"
send \"KEYS ban:*\n\"
expect \">\"
exit 0
"