#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"


export FLASK_APP=entangled.py
pipenv run flask run -p 7777
