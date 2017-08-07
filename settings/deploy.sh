#!/bin/bash
heroku run alembic upgrade head --remote $1 && git push heroku $2