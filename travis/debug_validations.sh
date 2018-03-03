#!/bin/bash

# Remove existing output
rm -f travis/*.json

## Get parent dir
DIR="$( cd "$( dirname `dirname "${BASH_SOURCE[0]}"` )" && pwd )"

## Force parent dir into python search path
export PYTHONPATH=$PYTHONPATH:$DIR

# Set scrapy settings
export SCRAPY_SETTINGS_MODULE='travis.travis_settings'

# Run new or modified spiders and save output
find documenters_aggregator/spiders -name "[^_]*.py" | \
    xargs basename -s .py | \
    xargs -I{} scrapy crawl {} -o ./travis/{}.json --loglevel=ERROR

# Validate saved output
find travis -name "*.json" | xargs -I{} invoke validate-spider {}
