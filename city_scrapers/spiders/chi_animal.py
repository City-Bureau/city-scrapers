# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import datetime
from dateutil.parser import parse as dateparse

from city_scrapers.constants import ADVISORY_COMMITTEE
from city_scrapers.spider import Spider


class ChiAnimalSpider(Spider):
    name = 'chi_animal'
    agency_name = 'Chicago Animal Care and Control Advisory Board'
    timezone = 'America/Chicago'
    allowed_domains = ['www.cityofchicago.org']
    start_urls = ['https://www.cityofchicago.org/city/en/depts/cacc/supp_info/public_notice.html']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('.page-full-description').css("ul").css("li"):
            # Pull the string
            try:
                text = item.xpath("text()").extract()[0]
            except IndexError:
                continue

            # Strip it
            text = text.strip()

            # Pass if there's nothing left
            if not text:
                continue

            # Parse the item
            data = {
                '_type': 'event',
                'name': 'Advisory Board Meeting',
                'event_description': self._parse_description(text),
                'classification': ADVISORY_COMMITTEE,
                'start': self._parse_start(text),
                'all_day': self._parse_all_day(text),
                'location': self._parse_location(text),
                'sources': self._parse_sources(response),
                'documents': self._documents(),
            }
            data['id'] = self._generate_id(data)
            data['status'] = self._parse_status(data)
            data['end'] = self._generate_end(data['start'])

            yield data

    def _parse_status(self, data):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        start_date = data['start']['date']
        today = datetime.date.today()
        if start_date < today:
            return 'passed'

        if start_date <= (today + datetime.timedelta(days=7)):
            return 'confirmed'

        return 'tentative'

    def _parse_location(self, item):
        """
        Parse or generate location.
        """
        return {
            'name': 'David R. Lee Animal Care Center',
            'address': '2741 S. Western Ave, Chicago, IL 60608',
        }

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to false.
        """
        return False

    def _parse_description(self, item):
        """
        Parse or generate event name.
        """
        return None

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        naive_datetime = self._naive_datetime_to_tz(dateparse(item))
        return {
            'date': naive_datetime.date(),
            'time': naive_datetime.time(),
        }

    def _generate_end(self, start):
        """
        Estimate end date and time.
        """
        start_dt = datetime.datetime.combine(start['date'], start['time'])
        end_dt = start_dt + datetime.timedelta(hours=3)
        return {
            'date': end_dt.date(),
            'time': end_dt.time(),
            'note': 'estimated 3 hours after the start time',
        }

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]

    def _documents(self):
        """
        Add standard documents.
        """
        return [{
            'url': (
                'https://www.cityofchicago.org/content/dam/city/depts/cacc/'
                'PDFiles/CACC_Commission_Meeting_Rules2.pdf'),
            'note': 'Commission Rules for Public Participation',
        }, {
            'url': (
                'https://www.cityofchicago.org/content/dam/city/depts/cacc/'
                'PDFiles/CACC_FAQs_prior_to_Jan_21_2016_revised_Sept2016.pdf'),
            'note': (
                'Answers to Frequently Asked Question at the Commission '
                'Meetings'),
        }]
