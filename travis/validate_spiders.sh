#!/bin/bash

# Remove existing output
rm -f travis/*.json

## Get parent dir
DIR="$( cd "$( dirname `dirname "${BASH_SOURCE[0]}"` )" && pwd )"

## Force parent dir into python search path
export PYTHONPATH=$PYTHONPATH:$DIR

# Set scrapy settings
export SCRAPY_SETTINGS_MODULE='travis.travis_settings'

# If not a PR build, exit
if [ $TRAVIS_PULL_REQUEST == 'false' ]; then echo "Build NOT triggered by a PR. Everything's ok."; exit 0; fi

# Run new or modified spiders and save output
git diff --name-only --diff-filter=AM $TRAVIS_COMMIT_RANGE| \
    grep .*documenters_aggregator/spiders/.*\.py | \
    xargs basename -s .py | \
    xargs -I{} scrapy crawl {} -o ./travis/{}.json --loglevel=ERROR

# Validate saved output
find travis -name "*.json" | xargs -I{} invoke validate-spider {}
