# City Scrapers

[![CI build status](https://github.com/City-Bureau/city-scrapers/workflows/CI/badge.svg)](https://github.com/City-Bureau/city-scrapers/actions?query=workflow%3ACI)
[![Cron build status](https://github.com/City-Bureau/city-scrapers/workflows/Cron/badge.svg)](https://github.com/City-Bureau/city-scrapers/actions?query=workflow%3ACron)

A collection of scrapers for public meetings in Cook County and Chicago, Illinois. Also includes scrapers for meetings of Illinois state boards.

## Getting Started

### Install

View our [installation guide](https://cityscrapers.org/docs/development/) for detailed instructions.

### Run

1. Activate the virtual environment:

```bash
pipenv shell
```

2. Run a scraper:

```bash
scrapy crawl <spider_name>
```

#### Example

To trigger the `chi_citycouncil` spider to scrape Chicago City Council meeting information and output the results to a JSON file:

```bash
scrapy crawl chi_citycouncil -O citycouncil.json
```

Alternatively, you can watch this [three minute video](https://www.youtube.com/watch?v=UgroG8CARWc) to see how to run a scraper.

### Test

1. If the virtual environment is not already active, activate it:

```bash
pipenv shell
```

2. Run all tests:
```bash
pytest
```

3. Run tests for a specific spider:
```bash
pytest tests/test_<spider_name>.py
```

#### Example

To run tests for the `chi_citycouncil` spider:

```bash
pytest tests/test_chi_citycouncil.py
```

### Windows support

Please note that if you're running this project on a Windows machine, you may need to install additional dependencies, such as [pywin32](https://pypi.org/project/pywin32/) or [pypiwin32](https://pypi.org/project/pypiwin32/).

## About this project

### What is City Scrapers?

This repo part of an initiative to scrape, store and publish meeting information for public meetings across the U.S. It's coordinated by the [City Bureau Documenters program](https://www.documenters.org/) and heavily driven by the open source community. We welcome contributions from everyone, especially those with little or no experience in tech and journalism.

### Why public meetings?

Public meetings are important spaces for democracy where any resident can participate and hold public figures accountable. Unfortunately, with the collapse of local news media in the U.S., hundreds of public meetings happen every week with no journalists in attendance. This means that residents are often unaware of the decisions being made in their area.

[City Bureau's Documenters program](https://www.documenters.org/) pays community members, called Documenters, an hourly wage to inform and engage their communities by attending and documenting public meetings.

A major challenge for Documenters is finding out when and where public meetings are happening and what's being discussed. Meeting information is typically spread across dozens of local government websites and rarely in useful data formats. This project was started in order to automatically fetch meeting information and store it in a central database so that a person doesn't have to do it manually.

In this repo, our scrapers fetch information about new meetings from the websites of the Chicago City Council, the Chicago Police Department, the Chicago Board of Education, and many more. Information about these meetings is published on [City Bureau's Documenters website](https://www.documenters.org/), where it can be used by Documenters and other residents.

### How can I help?

We welcome all contributions, including bug fixes, documentation improvements, and new scraper builds.

Since local government websites can change without warning, we particularly appreciate contributions that fix our scrapers when they break. 

If you want to help:

1. [Fill out this form](https://airtable.com/shrRv027NLgToRFd6) to join our Slack channel and meet the community.
2. Read about [how we collaborate](https://github.com/City-Bureau/city-scrapers/blob/main/CONTRIBUTING.md) and review our [Code of Conduct](https://github.com/City-Bureau/city-scrapers/blob/main/CODE_OF_CONDUCT.md).
3. Check out our [documentation](https://cityscrapers.org/docs/development/), and get started with [Installation](https://cityscrapers.org/docs/development/#installation) and [Contributing a spider](https://cityscrapers.org/docs/development/#contribute).

We ask all new contributors to start by writing a spider and its documentation or fixing a bug in order to gain familiarity with our code and culture. Reach out on Slack for support if you need it.

### Don't want to code?

[Join our Slack channel](https://airtable.com/shrRv027NLgToRFd6) (chatroom) to discuss ideas and meet the community!

A. We have ongoing conversations about what sort of data we should collect and how it should be collected. Help us make these decisions by commenting on [issues with a non-coding label](https://github.com/City-Bureau/city-scrapers/issues?q=is%3Aissue+is%3Aopen+label%3Anon-coding).

B. Research sources for public meetings. Answer questions like: Are we scraping events from the right websites? Are there local agencies that we're missing? Should events be updated manually or by a scraper? [Triage events sources on these issues](https://github.com/City-Bureau/city-scrapers/issues?q=is%3Aissue+is%3Aopen+label%3A%22non-coding%3A+triage+events+source%22).

### Community Mission

We hope that working with us will fill experience gaps (like using git/GitHub, working with data, or having your ideas taken seriously), so that more under-represented people will become decision-makers in both their community and the tech and media scenes at large.

### Support this work

This project is organized and maintained by [City Bureau](http://www.citybureau.org/).

- [Donate](https://www.citybureau.org/support)
- [Subscribe](https://citybureau.com/newsletter/)
- [Twitter @city_bureau](https://twitter.com/city_bureau/)
- [Facebook](https://www.facebook.com/CityBureau/)
