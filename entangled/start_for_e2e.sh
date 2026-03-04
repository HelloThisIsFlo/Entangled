#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"


cd $DIR/..
export FLASK_APP="entangled.server:initialize_app('e2e_tests')"
uv run flask run -p 7777
