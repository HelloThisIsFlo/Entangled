#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"


export FLASK_APP=entangled.py
#export FLASK_ENV=development
pipenv run flask run -p 7777
