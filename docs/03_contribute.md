---
title: Contribute
---

<h1 class="hidden">Contribute</h1>

## Familiarize yourself with how we work!

*Please read the project's [CONTRIBUTING.md](https://github.com/City-Bureau/city-scrapers/blob/master/CONTRIBUTING.md) file to learn about how we use GitHub to manage the project and our pull request policy.*

## Spider Set-up:

### 1. Find a site to scrape and create an issue

First, find an unclaimed event source within the project's [issues](https://github.com/City-Bureau/city-scrapers/issues). Any unassigned issue is fair game--assign yourself to pick up the work.

Save and note the issue number.

### 2. Create a new branch

Create a new branch in your fork:

```
$ git checkout -b XXXX-spider-NAMEOFAGENCY
```

`XXXX` is the zero-padded issue number and `NAMEOFAGENCY` should be something like `chi_housing`. For example, for ticket number 53 entitled "SPIDER: Chicago Housing Authority", create a branch named `0053-spider-chi_housing`.

### 3. Create a spider

Run the `genspider` task with a spider slug, spider name, and URLs to start scraping. Following the previous example:

```
(city-scrapers)$ invoke genspider chi_housing "Chicago Housing Authority" http://www.thecha.org
```

You should see some output like:

```
Created /Users/eads/Code/dcity-scrapers/documenters_aggregator/spiders/chi_housing.py
Created /Users/eads/Code/city-scrapers/tests/test_chi_housing.py
Created /Users/eads/Code/city-scrapers/tests/files/chi_housing_thecha.html
```

### 4. Test crawling

You now have a spider named `chi_housing`. To run it (admittedly, not much will happen until you start editing the scraper), run:

```
(city-scrapers)$ scrapy crawl chi_housing
```

If there are no error messages, congratulations! You have a barebones spider.
Additionally, each time you run your scraper, you can see your results as a csv output in the /documenters_aggregator/local_outputs/ folder. Each `scrapy crawl` command produces a unique file with the agency name and timestamp. These files are ignored by git, but you may want to clean the folder up locally after some testing.

### 5. Run the automated tests

We use the [pytest](https://docs.pytest.org/en/latest/) testing framework to
verify the behavior of the project's code and
[pyflakes](https://docs.pytest.org/en/latest/) and [pep8](https://pypi.python.org/pypi/pep8) to
check that all code is written in the proper style.

To run these tools, use the `invoke runtests` command:

```
(city-scrapers)$ invoke runtests
```

Whoops! The tests for new spiders fail by default. Here's typical output:

```
====================================== test session starts =======================================
platform darwin -- Python 3.6.2, pytest-3.1.3, py-1.4.34, pluggy-0.4.0
rootdir: /Users/eads/projects/city-scrapers, inifile:
collected 59 items

tests/test_chi_housing.py F
tests/test_idph.py .......................................................
tests/test_tasks.py ...

============================================ FAILURES ============================================
___________________________________________ test_tests ___________________________________________

    def test_tests():
        print('Please write some tests for this spider or at least disable this one.')
>       assert False
E       assert False

tests/test_chi_housing.py:8: AssertionError
-------------------------------------- Captured stdout call --------------------------------------
Please write some tests for this spider or at least disable this one.
============================== 1 failed, 58 passed in 0.95 seconds ==============================
```

That's OK.


## To Build a spider:

## A. Write parse methods in the spider

*If you run into any troubles, feel free to reach out on [slack](https://citybureau.slack.com/) or open a pull request so others can take a look at your code. Pull requests don't need to contain perfect code. See [CONTRIBUTING.md](https://github.com/City-Bureau/city-scrapers/blob/master/CONTRIBUTING.md).*

Open `documenters_aggregator/spiders/chi_housing.py` to work on your spider. A simple structure has been created for you to use. Let's look at the basics.

The spider should look something like this:

```python
# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy

from datetime import datetime


class Chi_housingSpider(scrapy.Spider):
    name = 'chi_housing'
    allowed_domains = ['thecha.org']
    start_urls = ['http://thecha.org']
    long_name = 'Chicago Housing Authority'

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

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
                'timezone': self._parse_timezone(item),
                'all_day': self._parse_all_day(item),
                'location': self._parse_location(item),
                'sources': self._parse_sources(item),
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

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return None

    # ...
```

The `Chi_housingSpider.parse(...)` method is a standard part of Scrapy and handles returning data in the correct format and any subsequent requests to be made.

There are pre-defined helper methods for every major field in the data. It's your job to fill them in. **See the [Event Schema](event-schema.md)** to see what is required in each field.

For example, `_parse_classification` could be:

```python
class Chi_housingSpider(scrapy.Spider):

    # ...

    def _parse_classification(self, item):
        """
        Parse or generate classification.
        """
        classification = item.css('.classification::text').extract_first()
        return classification

    # ...
```

## B. Write tests

Our general approach to writing tests is to save a copy of a site's HTML in
`tests/files` and then use that HTML to verify the behavior of each spider. In
this way, we avoid needing a network connection to run tests and our tests
don't break every time a site's content is updated.

Here is the test setup and an example test from the Idph spider:

```python
import pytest

from tests.utils import file_response
from documenters_aggregator.spiders.idph import IdphSpider

test_response = file_response('files/idph.html')
spider = IdphSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[2]['name'] == 'PAC: Maternal Mortality Review Committee Meeting'
```

It is also possible to execute a function over every element in the `parsed_items` list. In the following example, the `test_classification` function will be invoked once for each element in `parsed_items` list.

```python
@pytest.mark.parametrize('item', parsed_items)
def test_classification(item):
    assert item['classification'] == 'Not classified'
```

Parameterized test functions are best used to assert something about every event such as the existence of a field or a value all events will share.

You can read more about parameterized test functions [in the pytest docs](https://docs.pytest.org/en/latest/parametrize.html#pytest-mark-parametrize).

You generally want to verify that a spider:

* Extracts the correct number of events from a page.
* Extracts the correct values from a single event.
* Parses any date and time values, combining them as needed.

## C. Create a Pull Request

If your ready to submit your code to the project, you should create a pull
request on GitHub. You can do this as early as you would like in order to get
feedback from others working on the project. In this case, please prefix your
pull request name with `WIP` so that everyone knows what kind of feedback you
are looking for.

Additionally, please use the pull request description to explain anything you'd
like a reviewer to know about the code. See [CONTRIBUTING.md](https://github.com/City-Bureau/city-scrapers/blob/master/CONTRIBUTING.md) for more details.
