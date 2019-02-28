#!/bin/bash
scrapy runall -s LOG_ENABLED=False &

# Output to the screen every 9 minutes to prevent a travis timeout
# https://stackoverflow.com/a/40800348
export PID=$!
while [[ `ps -p $PID | tail -n +2` ]]; do
  echo 'Deploying'
  sleep 540
done
