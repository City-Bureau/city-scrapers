# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""

from datetime import datetime

from documenters_aggregator.spider import Spider


class Cook_electoralSpider(Spider):
    name = 'cook_electoral'
    long_name = 'Cook County Electoral Board'
    allowed_domains = ['cookcountyclerk.com']
    start_urls = ['http://cookcountyclerk.com/elections/electoralboard/Pages/default.aspx']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        row_names = response.xpath('//tr/@class').re(r'row\d+')
        for name in row_names:
            item = response.css('tr[class="{}"]'.format(name))
            data = {
                '_type': 'event',
                'name': self._parse_name(item),
                'description': self._parse_description(item, response),
                'classification': self._parse_classification(item),
                'start_time': self._parse_start(item),
                'end_time': None,
                'all_day': self._parse_all_day(item),
                'timezone': 'America/Chicago',
                'status': self._parse_status(item),
                'location': self._parse_location(item),
                'sources': self._parse_sources(response)
            }
            data['id'] = self._generate_id(data, data['start_time'])
            yield data

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).
        """
        return 'Not classified'

    def _parse_status(self, item):
        """
        If there is a link to case documents, return confirmed.
        Otherwise, return tentative.
        """
        if item.css('td > a::attr(href)').extract():
            return 'confirmed'
        else:
            return 'tentative'

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        return {
            'url': None,
            'name': item.css('td::text').extract()[-2].split('/')[1].strip(),
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
        }

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to false.
        """
        return False

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        texts = item.css('td::text').extract()
        contest = texts[2].strip()
        objector = texts[3].strip()
        candidate = texts[4].strip()
        name = ('Cook County Electoral Board Case; '
                'Contest: {0}; Objector: {1}; Candidate: {2}'.format(contest, objector, candidate))
        return name

    def _parse_description(self, item, response):
        """
        Parse or generate event name.
        """
        url_base = 'http://cookcountyclerk.com/elections/electoralboard/'
        return item.css('td > a::attr(href)').extract_first().replace('../', url_base)

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        start_string = ''.join(item.css('td > div::text').extract_first().strip().split())
        return self._make_date(start_string)

    def _make_date(self, datestring):
        """
        Combine year, month, day with variable time and export as timezone-aware,
        ISO-formatted string.
        """
        try:
            naive = datetime.strptime(datestring, '%m/%d/%Y%I:%M%p')
        except ValueError:
            return None
        else:
            self._naive_datetime_to_tz(naive)

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
