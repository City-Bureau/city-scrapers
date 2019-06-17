---
title: "Development"
permalink: /docs/development/
excerpt: "Intro to City Scrapers"
last_modified_at: 2018-10-04T20:15:56-04:00
toc: true
---

## Installation

Follow the following directions for cloning the repository and installing requirements.

### Prerequisites

- Git installed
- GitHub account
- Working internet connection
- Python 3.5, 3.6, or 3.7 installed
- Virtual environment manager (`pipenv`, `virtualenv`, `virtualenv-wrapper`, etc.)

If in doubt, please also refer to the [Setup Help](/docs/setup-help/), which should be useful for common first-time setup issues.

### Clone the Repository

**Note:** If you're interested in setting up and managing a group of scrapers for your area, follow these instructions for our [City-Bureau/city-scrapers-template](https://github.com/city-bureau/city-scrapers-template) repo instead.

These steps are the same, regardless of which option below you choose.

1. Fork the repository (either from the repo for the local City Scrapers project you're working on or [City-Bureau/city-scrapers](https://github.com/City-Bureau/city-scrapers))

2. Clone the fork to your local machine:

```bash
$ git clone https://github.com/YOUR-USERNAME/city-scrapers.git
```

3. Change directories into the main project folder:

```bash
$ cd city-scrapers
```

**If you do not plan on doing any development, you can skip creating a fork and just clone the repo**

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

**SKIP THIS section if `pipenv install` was successful**

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

### Windows Dependencies

If you're setting up the project in a Windows environment, you'll also need to install `pypiwin32`.

You can do this by running `pipenv install pypiwin32` for `pipenv` or installing normally with `pip install pypiwin32` in a virtual environment.

## Contribute

### Ways to contribute

There are many ways to contribute to this project: coding a spider (webscraper), building infrastructure, improving documentation, hosting in-person code evenings, and participating in technical discussions in [Slack](https://citybureau.slack.com/){:target="\_blank"} about code and design choices.

The best way to familiarize yourself with the code base is to build a spider. Follow the installation and contributing-a-spider sections below to get started. Reach out on Slack for support--we can meet up in person to troubleshoot some headaches like virtual environment issues.

To contribute infrastructure and utilities, see the [help-wanted GitHub issues](https://github.com/City-Bureau/city-scrapers/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22){:target="\_blank"}.

### Familiarize yourself with how we work!

**Please read the project's [`CONTRIBUTING.md`](https://github.com/City-Bureau/city-scrapers/blob/master/CONTRIBUTING.md){:target="\_blank"} file to learn about how we use GitHub to manage the project and our pull request policy.**

### Spider Setup

#### 1. Find a site to scrape and create an issue

First, find an unclaimed event source within the project's [issues](https://github.com/City-Bureau/city-scrapers/issues){:target="\_blank"}. Any unassigned issue is fair game. Add a comment indicating that you're interested in the work.

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
$ flake8
$ isort
$ yapf --in-place --recursive ./city_scrapers/ ./tests/
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
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiHousingSpider(CityScrapersSpider):
    name = 'chi_housing'
    agency = 'Chicago Housing Authority'
    timezone = 'America/Chicago'
    allowed_domains = ['thecha.org']
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

However, scheduling details like time and location should be pulled from the page, even if the value is always the same.

#### B. Write tests

Our general approach to writing tests is to save a copy of a site's HTML in `tests/files` and then use that HTML to verify the behavior of each spider. In this way, we avoid needing a network connection to run tests and our tests don't break every time a site's content is updated.

Here is the test setup and an example test:

```python
from datetime import datetime

import pytest
from freezegun import freeze_time
from tests.utils import file_response

from city_scrapers.spiders.chi_housing import ChiHousingSpider

test_response = file_response("files/chi_housing.html")
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

If your ready to submit your code to the project, you should create a pull request on GitHub. You can do this as early as you would like in order to get feedback from others working on the project. In this case, please mark your pull request as a [draft pull request](https://github.blog/2019-02-14-introducing-draft-pull-requests/){:target="\_blank"} when you create it. You can update this status when it is ready for review.

Additionally, please use the pull request description to explain anything you'd like a reviewer to know about the code. See [CONTRIBUTING.md](https://github.com/City-Bureau/city-scrapers/blob/master/CONTRIBUTING.md){:target="\_blank"} for more details.

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

`Meeting` objects accept the following values:

- `id`: `string` Unique identifier for the meeting based on its details, should be populated by `_get_id` method
- `title`: `string` Title of the individual meeting
- `description`: `string` Description of the specific meeting (not the overall agency) if available, otherwise empty string
- `classification`: `string` One of the [allowed classifications](#classifications) defined in `city_scrapers_core.constants` (`ADVISORY_COMMITTEE`, `BOARD`, `CITY_COUNCIL`, `COMMISSION`, `COMMITTEE`, `FORUM`, `POLICE_BEAT`, `NOT_CLASSIFIED`)
- `status`: `string` One of the [allowed statuses](#statuses) defined in `city_scrapers_core.constants`, should be populated by `_get_status` method (`CANCELLED`, `TENTATIVE`, `CONFIRMED`, `PASSED`)
- `start`: `datetime` Naive datetime object indicating the date and time when the meeting starts
- `end`: `datetime` Naive datetime object indicating the date and time the meeting ends
- `all_day`: `boolean` Whether the meeting takes place for an entire day
- `time_notes`: `string` Any additional notes on the timing of the meeting (i.e. if the start or end is estimated or subject to change)
- `location`: `dict` Dictionary with the keys `name` and `address` containing a location name (if available, otherwise an empty string) and the full address
- `links`: `list` List of dictionaries with the keys `title` (title/description of the link) and `href` (link URL) for all relevant links on the page, most importantly agenda and minutes if available
- `source`: `string` URL for meeting, typically a detail page if available otherwise the page it was scraped from

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

ASP.NET sites can be a challenge because they're often inconsistent and require maintaining a level of state across requests. You can see an example of handling this behavior in the `cook_electoral` spider.
