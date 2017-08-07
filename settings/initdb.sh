#!/bin/bash -e

#run heroku run setting/initdb.sh
alembic upgrade head
psql $DATABASE_URL -f settings/languages.sql
psql $DATABASE_URL -f settings/points_menu.sql