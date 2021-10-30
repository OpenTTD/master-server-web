#!/bin/sh

set -ex

if [ ! -e ".venv" ]; then
    python3 -m venv .venv
fi

# Install latest Python requirements
.venv/bin/pip install -r requirements.txt
