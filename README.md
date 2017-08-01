# Documenters Aggregator

A comprehensive, central, and accessible calendar for public government meetings in Chicago and Cook County.

## Prerequisites

You'll need a standard Python install. If you're on OS X, the [NPR Visuals guide](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html) is a good place to start, though you'll also need Python 3.x (which can be installed with `brew install python3` for Mac users).

### Requirements

* Python 3

## Installation

The following assumes you're using `virtualenv` and `virtualenv-wrapper`. Adjust accordingly if you aren't using these tools.

Optional but highly recommended: [Fork the repository](https://github.com/City-Bureau/documenters-aggregator/fork) to your own Github account.

```bash
mkvirtualenv -p `which python3` documenters-aggregator
git clone git@github.com:City-Bureau/documenters-aggregator.git
cd documenters-aggregator
pip install -r requirements.txt
```

If using a fork, replace `City-Bureau` above with your Github username.

## Creating a spider

_These instructions are a work-in-progress and completely provisional._

First, find an unclaimed event source in the [spreadsheet of event sources](http://www.cpsboe.org/meetings/planning-calendar).

Let's take the Chicago Public School Board of Education as an example. Assuming the status is "needs evaluation", you can start building a scraper.

Additional instructions to come.

## Spider architecture

This is what a basic HTML spider looks like:

```python
class IdphSpider(scrapy.Spider):
    name = 'idph'
    allowed_domains = ['www.dph.illinois.gov']
    start_urls = ['http://www.dph.illinois.gov/events']
    domain_root = 'http://www.dph.illinois.gov'

    def parse(self, response):
        for item in response.css('.eventspage'):
            yield {
                '_type': 'event',
                'id': self._get_event_id(item),
                'name': self._get_event_name(item),
                'description': self._get_event_description(item),
                'classification': self._get_classification(item),
                'start_time': self._get_event_start(item),
                'end_time': self._get_event_end(item),
                'all_day': self._get_all_day(item),
                'status': self._get_status(item),
                'location': self._get_location(item),
            }
        yield self._get_next(response)
```

The returned data should follow [the OpenCivicData event model](http://docs.opencivicdata.org/en/latest/data/event.html).
