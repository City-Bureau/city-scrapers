# Contributing a spider

## Find a site to scrape and create an issue

First, find an unclaimed event source in the [spreadsheet of event sources](https://docs.google.com/spreadsheets/d/1L1lbWj89wt8b2DIZhjxERJ5FCAWPDWd0nMibtc01sZk/edit#gid=0). Any scraper with a status of "needs evaluation" is fair game. If someone has already claimed the scraper, talk with them about joining their efforts.

Assuming you picked out a new one, create a [new issue](https://github.com/City-Bureau/documenters-aggregator/issues/new) with a title like "SPIDER: [name of agency]". Name of agency should be a fairly full name. "Chicago Housing Authority" is preferred over "CHA" in the issue title.

Save and note the issue number.

## Create a new branch

Create a new branch in your fork:

```
git checkout -b XXXX-spider-NAMEOFAGENCY
```

`XXXX` is the zero-padded issue number and `NAMEOFAGENCY` should be something like `cha`. For example, for ticket number 53 entitled "SPIDER: Chicago Housing Authority", create a branch named `0053-spider-cha`.

## Create a spider

Run the `genspider` task with a spider name and domain to scrape. Following the previous example:

```
invoke genspider cha www.thecha.org
```

You should see some output like:

```
Created /Users/eads/projects/documenters-aggregator/documenters_aggregator/spiders/cha.py
Created /Users/eads/projects/documenters-aggregator/tests/test_cha.py
```

## Test crawling

You now have a spider named `cha`. To run it (admittedly, not much will happen until you start editing the scraper), run:

```
scrapy crawl cha
```

## Run the automated tests

We use the [pytest](https://docs.pytest.org/en/latest/) testing framework to
verify the behavior of the project's code and 
[pyflakes](https://docs.pytest.org/en/latest/) and [pep8](https://pypi.python.org/pypi/pep8) to
check that all code is written in the proper style.

To run these tools, use the `invoke runtests` command:

```
invoke runtests
```

Whoops! The tests fail by default. Here's typical output:

```
====================================== test session starts =======================================
platform darwin -- Python 3.6.2, pytest-3.1.3, py-1.4.34, pluggy-0.4.0
rootdir: /Users/eads/projects/documenters-aggregator, inifile:
collected 59 items

tests/test_cha.py F
tests/test_idph.py .......................................................
tests/test_tasks.py ...

============================================ FAILURES ============================================
___________________________________________ test_tests ___________________________________________

    def test_tests():
        print('Please write some tests for this spider or at least disable this one.')
>       assert False
E       assert False

tests/test_cha.py:8: AssertionError
-------------------------------------- Captured stdout call --------------------------------------
Please write some tests for this spider or at least disable this one.
============================== 1 failed, 58 passed in 0.95 seconds ==============================
```

That's OK. Once you have passing tests, you can make a pull request.

## Write parse methods in the spider

Open `documenters_aggregator/spiders/cha.py` to work on your spider. A simple structure has been
created for you to use. Let's look at the basics and discuss advanced uses later.

The spider should look something like this:

```python
# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy

from datetime import datetime


class ChaSpider(scrapy.Spider):
    name = 'cha'
    allowed_domains = ['thecha.org']
    start_urls = ['http://thecha.org']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('.eventspage'):
            yield {
                '_type': 'event',
                'id': self._parse_id(item),
                'name': self._parse_name(item),
                'description': self._parse_description(item),
                'classification': self._parse_classification(item),
                'start_time': self._parse_start(item),
                'end_time': self._parse_end(item),
                'all_day': self._parse_all_day(item),
                'status': self._parse_status(item),
                'location': self._parse_location(item),
            }

        # self._parse_next(response) yields more responses to parse if necessary.
        # uncomment to find a "next" url
        # yield self._parse_next(response)

    def _parse_next(self, response):
        """
        Get next page. You must add logic to `next_url` and
        return a scrapy request.
        """
        next_url = None  # What is next URL?
        return scrapy.Request(next_url, callback=self.parse)

    def _parse_id(self, item):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        """
        return None

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).
        """
        return 'Not classified'

    # ...
```

The `ChaSpider.parse(...)` method is a standard part of Scrapy and handles returning data in the correct format and any subsequent requests to be made.

There are pre-defined helper methods for every major field in the data. It's your job to fill them in.

For example, `_parse_classification` could be:

```python
class ChaSpider(scrapy.Spider):

    # ...

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).
        """
        classification = item.css('.classification::text').extract_first()
        return classification

    # ...
```

## Write tests

TK TK writing tests
