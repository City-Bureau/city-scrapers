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

- Git installed
- GitHub account
- Working internet connection
- Python 3.5, 3.6, or 3.7 installed
- Virtual environment manager (`pipenv`, `virtualenv`, `virtualenv-wrapper`, etc.)

If in doubt, please also refer to the [Setup Help](/docs/setup-help/), which should be useful for common first-time setup issues.

### Windows Issues

Setting up a Python environment on Windows can be challenging at times, and while the installation instructions below should generally work, in the event of issues you can look at our guide on [setting up an environment on Codeanywhere](/docs/windows-setup/).

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

You'll need a fairly standard Python development stack. If you're on OS X, the [NPR Visuals Guide](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html){:target="\_blank"} is a good place to start, though you'll also need Python 3.x (which can be installed with `brew install python3` for Mac users).

### `pipenv` installation

[`pipenv`](https://pipenv.readthedocs.io/en/latest/) is package management tool for Python which combines managing dependencies and virtual environments. It's also designed to be compatible with Windows.

To setup an environment with `pipenv`, run:

```bash
$ pipenv install --dev --three
```

Then, you can either activate the virtual environment similarly to tools like `virtualenv-wrapper` by running

```bash
$ pipenv shell
```

after which all of your commands will be in a virtual environment. You can exit this environment by running `exit`, or by entering CTRL+D.

Alternatively, you can prefix commands with `pipenv run`. Here's an example that will run the Chicago Public Library scraper:

```bash
$ pipenv run scrapy crawl chi_library
```

### `virtualenv-wrapper` installation

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

There are many ways to contribute to this project: coding a spider (webscraper), building infrastructure, improving documentation, hosting in-person code evenings, and participating in technical discussions in [Slack](https://citybureau.slack.com/){:target="\_blank"} about code and design choices.

The best way to familiarize yourself with the code base is to build a spider. Follow the installation and contributing-a-spider sections below to get started. Reach out on Slack for support--we can meet up in person to troubleshoot some headaches like virtual environment issues.

To contribute infrastructure and utilities, see the [help-wanted GitHub issues](https://github.com/City-Bureau/city-scrapers/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22){:target="\_blank"}.

### Familiarize yourself with how we work!

**Please read the project's `CONTRIBUTING.md` file to learn about how we use GitHub to manage the project and our pull request policy.**

### Spider Setup

#### 1. Find a site to scrape and create an issues

First, find an unclaimed event source within the project's [issues](https://github.com/City-Bureau/city-scrapers/issues){:target="\_blank"}. Any unassigned issue is fair game. Add a comment indicating that you're interested in the work.

Save and note the issue number.

#### 2. Create a new branch

Create a new branch in your fork

```bash
$ git checkout -b XXXX-spider-NAMEOFAGENCY
```

`XXXX` is the zero-padded issue number and `NAMEOFAGENCY` should be something like `chi_housing`. For example, for ticket number 53 entitled "SPIDER: Chicago Housing Authority", create a branch named `0053-spider-chi_housing`.

#### 3. Create a spider

Create a spider from our tempalte with a spider slug, agency name, and a URL to start scraping. Inside your virtual environment following the previous examples (or prefixed by `pipenv run`) run:

```bash
(city-scrapers)$ python scripts/generate_spider.py chi_housing "Chicago Housing Authority" http://www.thecha.org
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

Additionally, if you uncomment `city_scrapers.pipelines.CsvPipeline` in `city_scrapers/settings/base.py`, each time you run your scraper you'll can see the results as CSV output in the `/city_scrapers/local_outputs/` folder. Each `scrapy crawl` command produces a unique file with the agency name and timestamp. These files are ignored by git, but you may want to clean the folder up locally after some testing.

#### 5. Run the automated tests

We use the [`pytest`](https://docs.pytest.org/en/latest/){:target="\_blank"} testing framework to verify the behavior of the project's code. To run this, simply run `pytest` in your project environment.

```bash
(city-scrapers)$ pytest
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

#### 6. Run linting and style-checking tools

We use [`flake8`](http://flake8.pycqa.org/en/latest/){:target="\_blank"}, [`isort`](https://isort.readthedocs.io/en/stable/){:target="\_blank"}, and [`yapf`](https://github.com/google/yapf){:target="\_blank"} to check that all code is written in the proper style. To run these tools individually, you can run the following commands:

```bash
$ flake8
$ isort
$ yapf --in-place --recursive ./city_scrapers/ ./deploy/ ./scripts/ ./tests/
```

Most text editors can be configured to fix style issues for you based off of the configuration settings in `setup.cfg`. Here's an example for VSCode using the [standard Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python){:target="\_blank"} (which can be modified/added at `.vscode/settings.json` in your project directory):

```json
{
  "python.pythonPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.envFile": "${workspaceRoot}/.env",
  "python.linting.flake8Args": ["--config", "${workspaceRoot}/setup.cfg"],
  "python.formatting.provider": "yapf",
  "python.formatting.yapfArgs": ["--style", "${workspaceRoot}/setup.cfg"],
  "python.sortImports.path": "${workspaceRoot}/setup.cfg",
  "editor.formatOnSave": true,
  "editor.rulers": [100]
}
```

This configuration will run linting and style checks for you, and also make necessary changes automatically any time you save. Packages are available for [Atom](https://atom.io/packages/linter-flake8){:target="\_blank"} and [Sublime Text](https://fosstack.com/setup-sublime-python/){:target="\_blank"} as well.

### Building a spider

#### A. Write parse methods in the spider

Open `city_scrapers/spiders/chi_housing.py` to work on your spider. A simple structure has been created for you to use. Let's look at the basics.

The spider should look something like this:

```python
# -*- coding: utf-8 -*-
from datetime import datetime

from city_scrapers.spider import Spider


class ChiHousingSpider(Spider):
    name = 'chi_housing'
    agency_name = 'Chicago Housing Authority'
    timezone = 'America/Chicago'
    allowed_domains = ['thecha.org']
    start_urls = ['http://thecha.org']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows a modified
        OCD event schema (docs/_docs/05-development.md#event-schema)

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('.eventspage'):
            data = {
                '_type': 'event',
                'name': self._parse_name(item),
                'event_description': self._parse_description(item),
                'classification': self._parse_classification(item),
                'start': self._parse_start(item),
                'end': self._parse_end(item),
                'all_day': self._parse_all_day(item),
                'location': self._parse_location(item),
                'documents': self._parse_documents(item),
                'sources': self._parse_sources(item),
            }

            data['status'] = self._generate_status(data)
            data['id'] = self._generate_id(data)

            yield data

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

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return ''

    def _parse_description(self, item):
        """
        Parse or generate event description.
        """
        return ''

    # ...
```

The `ChiHousingSpider.parse(...)` method is a standard part of Scrapy and handles returning data in the correct format and any subsequent requests to be made.

Every spider inherits from our custom `Spider` class, defined in `city_scrapers/spider.py` which adds some provides some of the helper functions like `_generate_id` and `_generate_status`.

There are pre-defined helper methods for every major field in the data. It's your job to fill them in. **See the Event Schema** to see what is required in each field.

For example, `_parse_name` could be:

```python
class ChiHousingSpider(Spider):

    # ...

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        name = item.css('.name::text').extract_first()
        return name

    # ...
```

Often a value for meetings returned by a spider will be the same regardless of meeting content (an example is that most meetings will always have `False` for the `all_day` value). In this case, feel free to remove the `_parse_*` method for that field, and simply include the value in each dictionary (so `'all_day': False` in this example rather than `'all_day': self._parse_all_day(item)`).

#### B. Write tests

Our general approach to writing tests is to save a copy of a site's HTML in `tests/files` and then use that HTML to verify the behavior of each spider. In this way, we avoid needing a network connection to run tests and our tests don't break every time a site's content is updated.

Here is the test setup and an example test:

```python
from datetime import date, time

import pytest
from freezegun import freeze_time
from tests.utils import file_response
from city_scrapers.spiders.chi_housing import ChiHousingSpider

test_response = file_response('files/chi_housing.html')
spider = ChiHousingSpider()

freezer = freeze_time('2018-10-12 12:00:00')
freezer.start()

parsed_items = [item for item in spider.parse(test_response) if isinstance(item, dict)]

freezer.stop()


def test_start():
    assert parsed_items[0]['start'] == {'date': date(2018, 1, 16), 'time': time(14, 0), 'note': ''}
```

You'll notice that the `freeze_time` function is called from the `freezegun` library before items are parsed from the spider. This is because some of our functions, `_generate_status` in particular, are time-sensitive and their outputs will change depending when they're executed. Calling `freeze_time` with the date the test HTML was initially scraped ensures that we will get the same output in our tests no matter when we run them.

It is also possible to execute a function over every element in the `parsed_items` list. In the following example, the `test_all_day` function will be invoked once for each element in `parsed_items` list.

```python
@pytest.mark.parametrize('item', parsed_items)
def test_all_day(item):
    assert item['all_day'] is False
```

Parameterized test functions are best used to assert something about every event such as the existence of a field or a value all events will share.

You can read more about parameterized test functions [in the pytest docs](https://docs.pytest.org/en/latest/parametrize.html#pytest-mark-parametrize){:target="\_blank"}.

You generally want to verify that a spider:

- Extracts the correct number of events from a page.
- Extracts the correct values from a single event.
- Parses any date and time values, combining them as needed.

#### C. Create a Pull Request

If your ready to submit your code to the project, you should create a pull request on GitHub. You can do this as early as you would like in order to get feedback from others working on the project. In this case, please prefix your pull request name with `WIP` so that everyone knows what kind of feedback you are looking for.

Additionally, please use the pull request description to explain anything you'd like a reviewer to know about the code. See [CONTRIBUTING.md](https://github.com/City-Bureau/city-scrapers/blob/master/CONTRIBUTING.md){:target="\_blank"} for more details.

## Event Schema

Our data model for events is based on the [Event object](http://docs.opencivicdata.org/en/latest/data/event.html){:target="\_blank"} from the [Open Civic Data](http://docs.opencivicdata.org){:target="\_blank"} project.

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

### Event Schema Guidelines

Since we're aggregating a wide variety of different types of meetings and information into a single schema, there are bound to be cases where the categories are unclear or don't seem to fit. Don't hesitate to reach out in a GitHub issue or on Slack if you aren't sure where certain information should go, but here are some additional notes on some of the schema attributes.

### Constants

When setting values for `classification` or `status` (although `status` should generally be set with the `_generate_status` method), you should import values from `city_scrapers/constants.py`. These constants are defined to avoid accidental mistakes like inconsistent capitalization or spelling for values that have a predefined list of options.

#### `name`

If the agency source supplies different names for each of its meetings, an example being the [Chicago Transit Authority](https://www.transitchicago.com/board/notices-agendas-minutes/) for the `chi_transit` spider, those names should be used here.

However, many agencies have a single standing meeting that we're scraping like [Detroit Eight Mile Woodward Corridor Improvement Authority](http://www.degc.org/public-authorities/emwcia/) for the `det_eight_mile_woodward_corridor_improvement_authority` spider. In this case, the Improvement Authority is the actual agency, but we're tracking meetings for the Board of Directors, so "Board of Directors" can be returned as the name.

There will be other cases where the information isn't entirely clear, and in general the approach should be to avoid repeating as much of the agency name in the meeting name as possible, and instead provide a more specific description where provided. So if the agency is the `Chicago Board of Directors for ...`, something like `Board of Directors` could still work as an abbreviated version.

#### `status`

Generally `status` should be set by passing the dictionary for a meeting to the `_generate_status` function. This checks when the meeting is in relation to the present time as well as if "canceled" or "rescheduled" appear in the meeting name or description. You can also provide values to the optional keyword argument `text` if there is additional text that may include one of those values and indicate a canceled meeting.

#### `event_description`

The event description should be filled by any additional information supplied by an agency website about a specific meeting. A generic description relating to the agency on a page should only be used if it looks like it can be changed on the meeting level (i.e. a description is duplicated on meeting detail pages). The idea behind this is that even if the description is usually the same, meeting-specific updates or cancellations would be captured by pulling those details.

For anything else, the `event_description` field should be left as an empty string `''`.

### Spider attributes

In addition, each spider records the following data as attributes:

```python
class ChiAnimalSpider(Spider):
    name = 'chi_animal'                                # name of spider in lowercase
    agency_name = 'Animal Care and Control Commission' # name of agency
    timezone = 'America/Chicago'                       # timezone of the events in tzinfo format
```

#### `agency_name`

The agency name initially supplied on creating the spider should be the overall governmental body that spider relates to, even if the body is already represented in another scraper. An example of this is in the `chi_schools`, `chi_school_actions`, and `chi_school_community_action_council` spiders. All of these spiders relate to different subdivisions of Chicago Public Schools, but they're split into separate spiders because they scrape different websites. In situations like this, the meeting name should clarify the subdivision holding the actual meeting, specifying the respective school actions and community action councils in this case.

## Scenarios

Many government websites share similar technology stacks, and we've built out some common approaches to a few of these.

### Legistar

Legistar is a software platform provided by Granicus that many governments use to hold their legislative information. If you run into a site using Legistar (typically you'll know because `legistar.com` will be in the URL), then you should use the `legistar` package to run the scraper and avoid unnecessary work. You can refer to spiders like `chi_parks` or `cook_board` to see examples of this approach.

### ASP.NET Sites

ASP.NET sites can be a challenge because they're often inconsistent and require maintaining a level of state across requests. You can see an example of handling this behavior in the `cook_electoral` spider.
