#!/bin/bash
set -ev

if [[ -f ".flake8" ]]; then
    wget https://raw.githubusercontent.com/mdolab/.github/master/.flake8 -O .flake8.temp;
    cat .flake8.temp >> .flake8;
    cat .flake8
else
    wget https://raw.githubusercontent.com/mdolab/.github/master/.flake8;
fi

flake8 . --count --show-source --statistics;
black . --check -l 120 --target-version py$PY;
