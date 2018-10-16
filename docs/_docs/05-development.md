---
title: "Development"
permalink: /docs/development/
excerpt: "Intro to City Scrapers"
last_modified_at: 2018-10-04T20:15:56-04:00
toc: true
---

## Installation

Follow the following directions for cloning the repository and installing requirements.

### Prequisites

* Git installed
* GitHub account
* Working internet connection
* Python 3.6 installed
* Virtual environment manager

If in doubt, please also refer to the SETUP HELP, which should be useful for common first-time setup issues.

### Windows Limitations

This project uses `invoke` tasks, which rely upon the `pty` package for pseudo-terminal utilties. Unfortunately, `pty` is not available on Windows, which makes it difficult to run all City Scraper tests locally. We recommend that if are using Windows and want to contribute more extensive code to the project to [set up an environment on Codeanywhere](/docs/windows-setup/). This is the simplest option to start contributing code.

If you don't mind some installation and want to develop locally, you can also consider creating a Linux environment by installing a virtual machine or partitioning your computer.

### Clone the Repository

These steps are the same, regardless of which option below you choose.

1. Fork the repository

2. Clone the fork to your local machine:

```bash
$ git clone https://github.com/YOUR-USERNAME/city-scrapers.git
```

3. Change directories into the main project folder:

```bash
$ cd city-scrapers
```

**If you do not plan on doing any development, you can skip creating a fork and just clone the main City Bureau repo**

## Local Python3 and Virtualenv

You'll need a fairly standard Python development stack, which Python 3.6 installed. If you're on OS X, the [NPR Visuals Guide](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html) is a good place to start, though you'll also need Python 3.x (which can be installed with `brew install python3` for Mac users).

The following assumes you have `virtualenv` and `virtualenv-wrapper` installed.
If you are using a different virtual environment manager, please refer to its
documentation (steps 1-3 should be the same).

1. Create a virtual environment (also called `city-scrapers`) for the project:

```bash
$ mkvirtualenv -p `which python3` city-scrapers
```

The virtual environment should now be activated.

2. Install the required packages into the virtual environment:

```bash
(city-scrapers)$ pip install -r requirements.txt
```

You should now have a working environment for running the project or making changes to it. Remember to always activate the virtual environment before working with it:

```bash
$ workon city-scrapers
```

Should you need to deactivate the virtual environment, it is as simple as:

```bash
(city-scrapers)$ deactivate
```

## Contribute

### Ways to contribute

There are many ways to contribute to this project: coding a spider (webscraper), building infrastructure, improving documentation, hosting in-person code evenings, and participating in technical discussions in [Slack](https://citybureau.slack.com/) about code and design choices.

The best way to familiarize yourself with the code base is to build a spider. Follow the installation and contributing-a-spider sections below to get started. Reach out on Slack for support--we can meet up in person to troubleshoot some headaches like virtual environment issues.

To contribute infrastructure and utilities, see the [help-wanted GitHub issues](https://github.com/City-Bureau/city-scrapers/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22).

### Familiarize yourself with how we work!

**Please read the project's `CONTRIBUTING.md` file to learn about how we use GitHub to manage the project and our pull request policy.**

### Spider Setup

#### 1. Find a site to scrape and create an issues

First, find an unclaimed event source within the project's [issues](https://github.com/City-Bureau/city-scrapers/issues). Any unassigned issue is fair game. Add a comment indicating that you're interested in the work.

Save and note the issue number.

#### 2. Create a new branch

Create a new branch in your fork

```bash
$ git checkout -b XXXX-spider-NAMEOFAGENCY
```

`XXXX` is the zero-padded issue number and `NAMEOFAGENCY` should be something like `chi_housing`. For example, for ticket number 53 entitled "SPIDER: Chicago Housing Authority", create a branch named `0053-spider-chi_housing`.

#### 3. Create a spider

Run the `genspider` task with a spider slug, spider name, and URL to start scraping. Following the previous example:

```bash
(city-scrapers)$ invoke genspider chi_housing "Chicago Housing Authority" http://www.thecha.org
```

You should see some output like:

```bash
Created /Users/eads/Code/city-scrapers/city_scrapers/spiders/chi_housing.py
Created /Users/eads/Code/city-scrapers/tests/test_chi_housing.py
Created /Users/eads/Code/city-scrapers/tests/files/chi_housing_thecha.html
```

#### 4. Test crawling

You now have a spider named `chi_housing`. To run it (admittedly, not much will happen until you start editing the scraper), run:

```bash
(city-scrapers)$ scrapy crawl chi_parks
```

If there are no error messages, congratulations! You have a barebones spider.

Additionally, each time you run your scraper, you can see your results as a csv output in the `/city_scrapers/local_outputs/` folder. Each `scrapy crawl` command produces a unique file with the agency name and timestamp. These files are ignored by git, but you may want to clean the folder up locally after some testing.

#### 5. Run the automated tests

We use the [`pytest`](https://docs.pytest.org/en/latest/) testing framework to verify the behavior of the project's code and [`pyflakes`](https://docs.pytest.org/en/latest/) and [`pep8`](https://pypi.python.org/pypi/pep8) to check that all code is written in the proper style.

To run these tools, use the `invoke runtests` command:

```bash
(city-scrapers)$ invoke runtests
```

Whoops! The tests for new spiders fail by default. Here's typical output:

```bash
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

### Building a spider

#### A. Write parse methods in the spider

Open `city_scrapers/spiders/chi_housing.py` to work on your spider. A simple structure has been created for you to use. Let's look at the basics.

The spider should look something like this:

```python
# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy

from datetime import datetime


class ChiHousingSpider(scrapy.Spider):
    name = 'chi_housing'
    allowed_domains = ['thecha.org']
    start_urls = ['http://thecha.org']
    agency_name = 'Chicago Housing Authority'

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
                'start': self._parse_start(item),
                'end': self._parse_end(item),
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

The `ChiHousingSpider.parse(...)` method is a standard part of Scrapy and handles returning data in the correct format and any subsequent requests to be made.

There are pre-defined helper methods for every major field in the data. It's your job to fill them in. **See the Event Schema** to see what is required in each field.

For example, `_parse_name` could be:

```python
class Chi_housingSpider(scrapy.Spider):

    # ...

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        name = item.css('.name::text').extract_first()
        return name

    # ...
```

#### B. Write tests

Our general approach to writing tests is to save a copy of a site's HTML in `tests/files` and then use that HTML to verify the behavior of each spider. In this way, we avoid needing a network connection to run tests and our tests don't break every time a site's content is updated.

Here is the test setup and an example test from the `Idph` spider:

```python
import pytest

from tests.utils import file_response
from city_scrapers.spiders.idph import IdphSpider

test_response = file_response('files/idph.html')
spider = IdphSpider()
parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]


def test_name():
    assert parsed_items[2]['name'] == 'PAC: Maternal Mortality Review Committee Meeting'
```

It is also possible to execute a function over every element in the `parsed_items` list. In the following example, the `test_all_day` function will be invoked once for each element in `parsed_items` list.

```python
@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] == False
```

Parameterized test functions are best used to assert something about every event such as the existence of a field or a value all events will share.

You can read more about parameterized test functions [in the pytest docs](https://docs.pytest.org/en/latest/parametrize.html#pytest-mark-parametrize).

You generally want to verify that a spider:

- Extracts the correct number of events from a page.
- Extracts the correct values from a single event.
- Parses any date and time values, combining them as needed.

#### C. Create a Pull Request

If your ready to submit your code to the project, you should create a pull request on GitHub. You can do this as early as you would like in order to get feedback from others working on the project. In this case, please prefix your pull request name with `WIP` so that everyone knows what kind of feedback you are looking for.

Additionally, please use the pull request description to explain anything you'd like a reviewer to know about the code. See [CONTRIBUTING.md](https://github.com/City-Bureau/city-scrapers/blob/master/CONTRIBUTING.md) for more details.

## Event Schema

Our data model for events is based on the [Event object](http://docs.opencivicdata.org/en/latest/data/event.html) from the [Open Civic Data](http://docs.opencivicdata.org) project.

"Required" means that the value cannot be `None`, an empty string, empty dictionary nor empty list. "Optional" means that `None` or empty values are ok.

```python
{
  '_type': 'event',                              # required value
  
  'id': 'unique identifier'                      # required string in format:
                                                # <spider-name>/<start-time-in-YYYYMMddhhmm>/<unique-id>/<underscored-event-name>
                                                # if start-time is missing, replace hhmm with 0000
                                                
  'name': 'Committee on Pedestrian Safety',      # required string, name of the event
  
  'event_description': 'A longer description',   # optional string, event description
  
  'all_day': False,                              # required boolean, whether or not the event lasts all day
  
  'status': 'tentative',                        # required string, one of the options in constants.py
                                                # 'canceled': event is listed as canceled or rescheduled
                                                # 'tentative': event both does not have an agenda and the event is > 7 days away
                                                # 'confirmed': either an agenda is posted or the event will happen in <= 7 days
                                                # 'passed': event happened in the past
  
  'classification': 'Board',                    # optional string. This field is used by some spiders
                                                # to differentiate between board and various committee
                                                # Options are defined in constants.py

  'start': {                                     # required dictionary
    'date': date(2018, 12, 31),                  # required datetime.date object in local timezone
    'time': None,                                # optional datetime.time object in local timezone
    'note': 'in the afternoon'                   # optional string, supplementary information if there's no start time
  },
  
  'end': {                                       # required dictionary
    'date': date(2018, 12, 31),                  # optional datetime.date object in local timezone
    'time': time(13, 30),                        # optional datetime.time object in local timezone
    'note': 'estimated 2 hours after start time' # optional string, supplementary information if there's no end time
  },   

  'location': {                                  # required dict of event locations
                                                # for multiple locations: make a different event with unique id for each location
    'address': '121 N LaSalle Dr, Chicago, IL',  # required string, address of the location
    'name': 'City Hall, Room 201A',              # optional string, name of the location
    'neighborhood': 'Loop'                       # optional string, use community area in Chicago
  },
  
  'documents': [                                 # optional list of documents
    {
      'url': 'http://www.example.com/agenda.pdf',# required string, URL to the document
      'note': 'agenda'                           # required string, name of the document
    }
  ],

  'sources': [                                   # required list of sources
    {
      'url': '',                                 # required string, URL where data was scraped from
      'note': ''                                 # optional string, info about how the data was scraped
    }
  ]
}
```

### Spider attributes

In addition, each spider records the following data as attributes:

```python
class ChiAnimalSpider(Spider):
    name = 'chi_animal'                              # name of spider in lowercase
    agency_name = 'Animal Care and Control Commission' # name of agency
    timezone = 'America/Chicago'                     # timezone of the events in tzinfo format
```
