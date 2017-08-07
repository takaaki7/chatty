#!/bin/bash
#use this in wercker container
. /pipeline/source/venv/bin/activate
. /pipeline/source/env/werckerenv
alembic revision --autogenerate -m $1