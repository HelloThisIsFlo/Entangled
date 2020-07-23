#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

function create_app_tkinter_version() {
    # Prompting for sudo pass
    sudo echo ""

    pipenv run pyinstaller -w $DIR/sandbox.py

    # Fix TCL bug: https://jacob-brown.github.io/2019-09-10-pyinstaller#macos
    # Not needed if not using tkinter
    sudo python $DIR/TCLChanger/TCLChanger.py
}

function create_app() {
    pipenv run pyinstaller -w --onefile $DIR/sandbox.py
}

function build_dmg() {
    # NPM Tool - Install if needed: 'npm install -g appdmg'
    # Repo: https://github.com/LinusU/node-appdmg
    appdmg $DIR/appdmg.json $DIR/dist/sandbox.dmg
}

function cleanup() {
    rm -rf $DIR/build $DIR/dist
}

function show_result() {
    open $DIR/dist
}

cleanup
create_app
build_dmg
show_result
