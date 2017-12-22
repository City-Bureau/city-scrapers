#!/bin/bash

# Remove existing output
rm scripts/*.json

# Run scrapers that have changed
git diff --name-only --diff-filter=AM HEAD...$TRAVIS_BRANCH | \
    grep .*documenters_aggregator/spiders/.*\.py | \
    xargs -I{} sh -c 'scraper=$(basename "${1%%.*}") ; scrapy crawl $scraper -o ./scripts/$scraper.json --loglevel=ERROR' -- {}

# Validate any changed scrapers
ls scripts/*.json | xargs -I{} sh -c 'invoke validate-spider $(basename "${1%%.*}")' -- {}
