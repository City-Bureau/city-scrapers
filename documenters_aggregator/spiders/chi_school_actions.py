# -*- coding: utf-8 -*-

from datetime import datetime
from pytz import timezone
from documenters_aggregator.spider import Spider


class ChiSchoolActionsSpider(Spider):
    name = 'chi_school_actions'
    long_name = 'Chicago Public Schools: School Actions'
    allowed_domains = ['schoolinfo.cps.edu']
    start_urls = ['http://schoolinfo.cps.edu/SchoolActions/Documentation.aspx']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.gitbooks.io/documenters-event-aggregator/event-schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for school in response.css('#wrapper > table > tr'):
            school_name = school.css('td:first-child span::text').extract_first()
            school_action = school.css('td:nth-child(2) p > span::text').extract_first().strip()
            ## TODO: Multiple links to documents, is there a place to include those?

            for meeting_section in school.css('#main-body > table > tr > td > table > tr'):
                meeting_type = self._parse_classification(meeting_section)
                for meeting in meeting_section.css('td > table'):
                    start_datetime = self._parse_start(meeting)
                    end_datetime = self._parse_end(meeting)
                    item_name = self._parse_name(school_name, meeting_type)
                    yield {
                        '_type': 'event',
                        'id': self._generate_id({'name': item_name}, start_datetime),
                        'name': item_name,
                        'description': self._parse_description(school_name, school_action, meeting_type),
                        'classification': meeting_type,
                        'start_time': self._format_datetime(start_datetime),
                        'end_time': self._format_datetime(end_datetime),
                        'timezone': self._parse_timezone(meeting),
                        'all_day': False,
                        'location': self._parse_location(meeting),
                        'sources': self._parse_sources(),
                    }

    def _parse_name(self, school_name, meeting_type):
        """
        Parse or generate event name.
        """
        return '{} {}'.format(school_name, meeting_type)

    def _parse_description(self, school_name, school_action, meeting_type):
        """
        Parse or generate event description.
        """
        return '{} {}: {}'.format(school_name, school_action, meeting_type)

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        return item.css('td > p.sub-title:first-of-type::text').extract_first()

    def _parse_date_str(self, item):
        """
        Parse date, return as %Y-%b-%d string
        """
        year = item.css('.year::text').extract_first()
        month = item.css('.month::text').extract_first()
        day = item.css('.day::text').extract_first()
        return '{}-{}-{}'.format(year, month, day)

    def _parse_datetime_str(self, date_str, time_str):
        """
        Parse datetime string from date and time strings
        """
        time_str = time_str.strip().replace('.', '')[:]
        # Enforce max length, select format string
        if ':' in time_str:
            time_str = time_str[:7]
            time_format_str = '%I:%M %p'
        else:
            time_str = time_str[:4]
            time_format_str = '%I %p'
        return datetime.strptime(date_str + time_str, '%Y-%b-%d' + time_format_str)

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        date_str = self._parse_date_str(item)
        time = item.css('.time::text').extract_first()
        return self._parse_datetime_str(date_str, time.split('-')[0])

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        date_str = self._parse_date_str(item)
        time = item.css('.time::text').extract_first()
        split_time = time.split('-')
        if len(split_time) > 1:
            return self._parse_datetime_str(date_str, split_time[1])
        else:
            return self._parse_start(item)

    def _format_datetime(self, time):
        """
        Format datetime as timezone-aware,
        ISO-formatted string.
        """
        tz = timezone('America/Chicago')
        return tz.localize(time).isoformat()

    def _parse_timezone(self, item):
        """
        Parse or generate timzone in tzinfo format.
        """
        return 'America/Chicago'

    def _parse_location(self, item):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        return {
            'url': '',
            'name': item.css('.addr::text').extract_first(),
            'address': item.css('.addr2::text').extract_first(),
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
        }

    def _parse_sources(self):
        """
        Parse or generate sources.
        """
        return [{'url': self.start_urls[0], 'note': ''}]
