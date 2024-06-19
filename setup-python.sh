#!/bin/bash

set -e

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

yes | sudo apt install python3-venv

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt
