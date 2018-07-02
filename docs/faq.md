---
---

# FAQ

## What if the dates I want to scrape are only available inside a PDF or image?

In this case, comment or make a note on the source spreadsheet. We will have
a process for manually updating some data sources. At this point in time, we'll
use the manual process for PDFs and images.

## How do I run a spider (like [ward_night](https://github.com/City-Bureau/city-scrapers/blob/master/city_scrapers/spiders/ward_night.py) or [chi_localschoolcouncil](https://github.com/City-Bureau/city-scrapers/blob/master/city_scrapers/spiders/chi_localschoolcouncil.py)) that requires a Google Sheets API key?

You can get an API key for Google Sheets for free by:

- Logging into the Google API Console, choosing "Enabled APIs and services", and then searching for "Sheets API", selecting "Google Sheets API", and then clicking "ENABLE".
- Then, in the left sidebar, choose "Credentials" and then "CREATE CREDENTIALS" -> "API Key". You will be shown a key that you can save somewhere safe.

You'll need to set this as an environment variable before running the new scraper. An easy way to do this is to just put it on the command line like so:

```
$ CITY_SCRAPERS_GOOGLE_API_KEY=TheTokenYouCreatedAbove scrapy crawl chi_localschoolcouncil
```