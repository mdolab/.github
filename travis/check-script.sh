#!/bin/bash
set -ev

# don't download the reference flake8 config if one already exists in the repo
if [[ !-f ".flake8" ]]; then
    wget https://raw.githubusercontent.com/mdolab/.github/master/.flake8;
fi

flake8 . --count --show-source --statistics;
black . --check -l 120 --target-version py$PY;
