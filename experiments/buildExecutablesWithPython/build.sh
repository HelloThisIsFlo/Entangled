#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"


rm -rf $DIR/build $DIR/dist

# Prompting for sudo pass
sudo echo ""

pyinstaller -w $DIR/sandbox.py

# Fix TCL bug: https://jacob-brown.github.io/2019-09-10-pyinstaller#macos
# Not needed if not using tkinter
sudo python $DIR/TCLChanger/TCLChanger.py
