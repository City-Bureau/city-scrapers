---
title: "Development"
permalink: /docs/development/
excerpt: "City Scrapers development documentation"
last_modified_at: 2018-10-04T20:15:56-04:00
toc: true
---

## Setup

Follow the following directions for cloning the repository and installing requirements.

### What you'll need

- [Git](https://git-scm.com/)
- [GitHub](https://github.com/) account
- Working internet connection
- [Python](https://www.python.org/) 3.5, 3.6, or 3.7 installed
- [Pipenv](https://pipenv.readthedocs.io/en/latest/) for managing dependencies and virtual environments

You can find more details on setting up these tools and other common issues in [Setup Help](/docs/setup-help/).

### Clone the Repository

**Note:** If you're interested in setting up and managing a group of scrapers for your area, follow these instructions for our [City-Bureau/city-scrapers-template](https://github.com/city-bureau/city-scrapers-template) repo instead.

These steps are the same, regardless of which option below you choose.

#### 1. Fork the repository

This can be from the repo for the local City Scrapers project you're working on or [City-Bureau/city-scrapers](https://github.com/City-Bureau/city-scrapers).

#### 2. Clone the fork to your local machine

```bash
$ git clone https://github.com/YOUR-USERNAME/city-scrapers.git
```

#### 3. Change directories into the main project folder

```bash
$ cd city-scrapers
```

### Install dependencies

[Pipenv](https://pipenv.readthedocs.io/en/latest/) is package management tool for Python which combines managing dependencies and virtual environments. It's also designed to be compatible with Windows. Other tools like `virtualenv` and `virtualenv-wrapper` can be used, but our documentation will only refer to Pipenv since it's quickly being adopted as the standard for Python dependency management.

To setup an environment with Pipenv, run:

```bash
$ pipenv sync --dev --three
```

Then, you can activate the virtual environment by running:

```bash
$ pipenv shell
```

after which all of your commands will be in a virtual environment. You can exit this environment by running `exit`, or by entering CTRL+D.

Alternatively, you can prefix commands with `pipenv run`. Here's an example that will run the Chicago Public Library scraper:

```bash
$ pipenv run scrapy crawl chi_library
```

## Contribute

### Ways to contribute

There are many ways to contribute to this project: coding a spider (webscraper), building infrastructure, improving documentation, hosting in-person code evenings, and participating in technical discussions in [Slack](https://citybureau.slack.com/){:target="\_blank"} about code and design choices. Request an invite to our Slack by filling out [this form](https://airtable.com/shrRv027NLgToRFd6){:target="\_blank"}.

The best way to familiarize yourself with the code base is to build a spider. Follow the installation and contributing-a-spider sections below to get started. Reach out on Slack for support.

### Familiarize yourself with how we work

Please read the project's [`CONTRIBUTING.md`](https://github.com/City-Bureau/city-scrapers/blob/master/CONTRIBUTING.md){:target="\_blank"} file to learn about how we use GitHub to manage the project and our pull request policy.

### Spider Setup

#### 1. Find an open issue to work on

First, find an issue labeled "help wanted" within the project's [issue tracker](https://github.com/City-Bureau/city-scrapers/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22){:target="\_blank"}. Any issue without the "claimed" label is fair game. Add a comment indicating that you're interested in the work, and once a maintainer has replied and marked the issue "claimed" you're good to go.

Save and note the issue number.

#### 2. Create a new branch

Create a new branch in your fork

```bash
$ git checkout -b XXXX-spider-NAMEOFAGENCY
```

`XXXX` is the zero-padded issue number and `NAMEOFAGENCY` should be something like `chi_housing`. For example, for ticket number 53 entitled "SPIDER: Chicago Housing Authority", create a branch named `0053-spider-chi_housing`.

#### 3. Create a spider

Create a spider from our template with a spider slug, agency name, and a URL to start scraping. Inside your virtual environment following the previous examples (or prefixed by `pipenv run`) run:

```bash
(city-scrapers)$ scrapy genspider chi_housing "Chicago Housing Authority" http://www.thecha.org
```

You should see some output like:

```bash
Created file: /Users/eads/Code/city-scrapers/city_scrapers/spiders/chi_housing.py
Created file: /Users/eads/Code/city-scrapers/tests/test_chi_housing.py
Created file: /Users/eads/Code/city-scrapers/tests/files/chi_housing.html
```

#### 4. Test crawling

You now have a spider named `chi_housing`. To run it (admittedly, not much will happen until you start editing the scraper), run:

```bash
(city-scrapers)$ scrapy crawl chi_housing
```

If there are no error messages, congratulations! You have a barebones spider.

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
$ pipenv run flake8
$ pipenv run isort
$ pipenv run style
```

Most text editors can be configured to fix style issues for you based off of the configuration settings in `setup.cfg`. See an example of this for VSCode in [Setup Help](/docs/setup-help/).

### Building a spider

#### A. Write parse methods in the spider

Open `city_scrapers/spiders/chi_housing.py` to work on your spider. A simple structure has been created for you to use. Let's look at the basics.

The spider should look something like this:

```python
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiHousingSpider(CityScrapersSpider):
    name = 'chi_housing'
    agency = 'Chicago Housing Authority'
    timezone = 'America/Chicago'
    start_urls = ['http://thecha.org']

    def parse(self, response):
        """
        `parse` should always `yield` a Meeting item.

        Change the `_parse_id`, `_parse_title`, etc methods to fit your scraping
        needs.
        """
        for item in response.css(".meetings"):
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return ""

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    # ...
```

The `ChiHousingSpider.parse(...)` method is a standard part of Scrapy and handles returning data in the correct format and any subsequent requests to be made.

Every spider inherits from our custom `CityScrapersSpider` class, defined in the `city_scrapers_core` package which adds some provides some of the helper functions like `_get_id` and `_get_status`. Each spider should yield `Meeting` items in the `parse` method (or another helper method depending on the page). See a more [detailed description of `Meeting` items below](#meeting-items).

There are pre-defined helper methods for every major field in the data. It's your job to fill them in.

For example, `_parse_title` could be:

```python
class ChiHousingSpider(Spider):

    # ...

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        title = item.css(".title::text").extract_first()
        return title

    # ...
```

Often a value for meetings returned by a spider will be the same regardless of meeting content (an example is that most meetings will always have `False` for the `all_day` value). For fields like `classification`, `all_day`, and `title` (sometimes), feel free to remove the `_parse_*` method for that field, and simply include the value in each dictionary (so `'all_day': False` in this example rather than `'all_day': self._parse_all_day(item)`).

However, scheduling details like time and location should be pulled from the page, even if the value is always the same. In some cases it can be easier to make sure that an expected value is there and raise an error if not than to parse it every time. An example of raising an error if information has changed can be found in [`chi_license_appeal`](https://github.com/City-Bureau/city-scrapers/blob/bb127e3c4243bf7bf9aa59cf7a7b4b43d1d48c0a/city_scrapers/spiders/chi_license_appeal.py#L67-L70)

#### B. Write tests

Our general approach to writing tests is to save a copy of a site's HTML in `tests/files` and then use that HTML to verify the behavior of each spider. In this way, we avoid needing a network connection to run tests and our tests don't break every time a site's content is updated.

Here is the test setup and an example test:

```python
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.chi_housing import ChiHousingSpider

test_response = file_response(
    join(dirname(__file__), "files", "chi_housing.html"),
    url="https://www.thecha.org/"
)
spider = ChiHousingSpider()

freezer = freeze_time("2018-10-12")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_start():
    assert parsed_items[0]["start"] == datetime(2018, 1, 16, 14, 0)
```

You'll notice that the `freeze_time` function is called from the `freezegun` library before items are parsed from the spider. This is because some of our functions, `_get_status` in particular, are time-sensitive and their outputs will change depending when they're executed. Calling `freeze_time` with the date the test HTML was initially scraped ensures that we will get the same output in our tests no matter when we run them.

It is also possible to execute a function over every element in the `parsed_items` list. In the following example, the `test_all_day` function will be invoked once for each element in `parsed_items` list.

```python
@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
```

Parameterized test functions are best used to assert something about every event such as the existence of a field or a value all events will share.

You can read more about parameterized test functions [in the pytest docs](https://docs.pytest.org/en/latest/parametrize.html#pytest-mark-parametrize){:target="\_blank"}.

You generally want to verify that a spider:

- Extracts the correct number of events from a page.
- Extracts the correct values from a single event.
- Parses any date and time values, combining them as needed.

#### C. Create a Pull Request

If your ready to submit your code to the project, you should create a pull request on GitHub. You can do this as early as you would like in order to get feedback from others working on the project.

When you go to open a pull request, you'll see a template with details pre-populated including a checklist of tasks to complete. Fill out the information as best you can (it's alright if you can't check everything off yet). It's designed to provide some reminders for tasks to complete as well as making review easier. You can use the rest of the description to explain anything you'd like a reviewer to know about the code. See [CONTRIBUTING.md](https://github.com/City-Bureau/city-scrapers/blob/master/CONTRIBUTING.md){:target="\_blank"} for more details.

### `Meeting` Items

The `Meeting` items you need to return are derived from Scrapy's [`Item` classes](https://docs.scrapy.org/en/latest/topics/items.html). The original source can be found in the [`city_scrapers_core` package](https://github.com/City-Bureau/city-scrapers-core/blob/master/city_scrapers_core/items.py).

A Scrapy `Item` mostly functions like a normal Python `dict`. You can create a `Meeting` Item with Python keyword arguments and also set values after it's created with Python's general `dict` syntax:

```python
meeting = Meeting(
    title='Board of Directors',
    description='',
)  # This creates a Meeting
meeting['source'] = 'https://example.com'  # This sets a value on the Meeting
```

Each of the values in `Meeting` should adhere to some guidelines.

#### `id`

Unique identifier for a meeting created from the scraped its scraped details. This should almost always be populated by the `_get_id` method inherited from `CityScrapersSpider` and not set directly.

#### `title`

The title of an individual instance of a meeting. Because most of the meetings we're scraping occur on a regular basis, sometimes this is alright to set statically if we can be reasonably certain that it won't change. Some common examples are "Board of Directors" or "Finance Committee".

#### `description`

A string describing the specific meeting (not the overall agency). This usually isn't available, and in that case it should default to an empty string.

#### `classification`

One of the [allowed classification constants](#classifications) describing the type of the meeting.

#### `status`

One of the [allowed status constants](#statuses) describing the meeting's current status. Generally you shouldn't edit this other than to set it with the `_get_status` method which checks the meeting title and description for any indication of a cancellation. If there is relevant text in a meeting's description (like "CANCELLED" displaying next to the meeting name outside of the title) you can pass it to the `_get_status` method as a keyword argument like this:

```python
meeting["status"] = self._get_status(item, text="Meeting is cancelled")
```

#### `start`

Naive `datetime` object indicating the date and time a meeting will start. The agency's timezone (from the spider's `timezone` property) will be applied in the pipelines, so that doesn't need to be managed in the spider. All spiders should have a value for `start`, and if a time is unavailable and there are no sensible defaults it should be listed as 12:00 am.

#### `end`

Naive `datetime` or `None` indicating the date and time a meeting will end. This is most often not available, but otherwise the same rules apply to it as `start`.

#### `all_day`

Boolean indicating whether or not the meeting occurs all day. It's mostly a carryover from the [Open Civic Data event specification](https://opencivicdata.readthedocs.io/en/latest/data/event.html), and is almost always set to `False`.

#### `time_notes`

String indicating anything people should know about the meeting's time. This can be anything from indicating that a meeting will start immediately following the previous one (so the time might not be accurate) or a general indication to double-check the time if the agency suggests that attendees should confirm in advance.

#### `location`

Dictionary with required `name` and `address` strings indicating where the meeting will take place. Either or both values can be empty strings, but if no location is available either a default should be found (most meetings have usual locations) or `TBD` should be listed as the `name`. If a meeting has a standing location that is listed separate from individual meetings, creating a [`_validate_location`](https://github.com/City-Bureau/city-scrapers/blob/20a12ba5d76186cba65b45f7f764f02393d4a991/city_scrapers/spiders/chi_ssa_34.py#L57-L59) that checks whether the meeting location has changed (and returns an error if it has) can be sometimes be more straightforward than trying to parse the same location each time.

```python
{
    "name": "City Hall",
    "address": "1234 Fake St, Chicago, IL 60601"
}
```

#### `links`

A list of dictionaries including values `title` and `href` for any relevant links like agendas, minutes or other materials. The `href` property should always return the full URL and not relative paths like `/doc.pdf`.

#### `source`

The URL the meeting was scraped from, which will almost always be `response.url` with the exception of scraping some lists with detail pages.

Since we're aggregating a wide variety of different types of meetings and information into a single schema, there are bound to be cases where the categories are unclear or don't seem to fit. Don't hesitate to reach out in a GitHub issue or on Slack if you aren't sure where certain information should go.

### Constants

When setting values for `classification` or `status` (although `status` should generally be set with the `_get_status` method), you should import values from `city_scrapers_core.constants`. These constants are defined to avoid accidental mistakes like inconsistent capitalization or spelling for values that have a predefined list of options.

#### Classifications

- `ADVISORY_COMMITTEE`: Advisory Committees or Councils (often Citizen's Advisory Committees)
- `BOARD`: Boards of Trustees, Directors, etc.
- `CITY_COUNCIL`: Legislative branch of a local government
- `COMMISSION`: Any agency with "commission" in the name
- `COMMITTEE`: Committees of larger agencies
- `FORUM`: Public hearings, community input meetings, informational meetings etc.
- `POLICE_BEAT`: Specifically used for police beat meetings
- `NOT_CLASSIFIED`: Anything that doesn't seem to fit well into any of the prior categories

#### Statuses

- `CANCELLED`
- `TENTATIVE`
- `CONFIRMED`
- `PASSED`

### Spider attributes

In addition, each spider records the following data as attributes:

```python
class ChiAnimalSpider(CityScrapersSpider):
    name = "chi_animal"                                    # name of spider in lowercase
    agency = "Chicago Animal Care and Control Commission"  # name of agency
    timezone = "America/Chicago"                           # timezone of the events in tzinfo format
```

#### `agency`

The agency name initially supplied on creating the spider should be the overall governmental body that spider relates to, even if the body is already represented in another scraper. An example of this is in the `chi_schools`, `chi_school_actions`, and `chi_school_community_action_council` spiders. All of these spiders relate to different subdivisions of Chicago Public Schools, but they're split into separate spiders because they scrape different websites. In situations like this, the meeting name should clarify the subdivision holding the actual meeting, specifying the respective school actions and community action councils in this case.

## Scenarios

Many government websites share similar technology stacks, and we've built out some common approaches to a few of these.

### Legistar

Legistar is a software platform provided by Granicus that many governments use to hold their legislative information. If you run into a site using Legistar (typically you'll know because `legistar.com` will be in the URL), then you should use the `legistar` package to run the scraper and avoid unnecessary work. You can refer to spiders like `chi_parks` or `cook_board` to see examples of this approach.

### ASP.NET Sites

ASP.NET sites can be a challenge because they're often inconsistent and require maintaining a level of state across requests. You can see an example of handling this behavior in the [`cuya_administrative_rules`](https://github.com/City-Bureau/city-scrapers-cle/blob/master/city_scrapers/spiders/cuya_administrative_rules.py) spider.
