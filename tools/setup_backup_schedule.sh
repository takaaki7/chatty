#!/bin/bash
heroku pg:backups:schedule DATABASE_URL --at '15:00 Asia/Tokyo' --app chatty-bot-prod
