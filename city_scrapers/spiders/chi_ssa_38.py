# -*- coding: utf-8 -*-
from city_scrapers.spider import Spider
import re
from datetime import datetime

class ChiSsa38Spider(Spider):
    name = 'chi_ssa_38'
    agency_name = 'Chicago Special Service Area #38 Northcenter'
    timezone = 'America/Chicago'
    allowed_domains = ['www.northcenterchamber.com']
    start_urls = ['http://www.northcenterchamber.com/pages/MeetingsTransparency1']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows a modified
        OCD event schema (docs/_docs/05-development.md#event-schema)

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        # Get first meeting, watch out for noon

        text = response.xpath("//text()").extract()
        links = response.xpath("//a[@href]").extract()
        next_data = self._parse_first(text, links)
        if next_data is not None:  # In case next meeting is not specified
            yield next_data

        strongtext = response.xpath("//strong").extract()
        meetings = [x for x in strongtext if "href" in x and "Minutes" in x]
        for meeting in meetings:
            data = {
                '_type': 'event',
                'name': self._parse_name(meeting),
                'event_description': self._parse_description(meeting),
                'classification': self._parse_classification(meeting),
                'start': self._parse_start(meeting),
                'all_day': False,
                'location': self._parse_location(meeting),
                'documents': self._parse_documents(meeting),
                'sources': [{
                        'url': response.url,
                        'note': ''
                    }]
            }

            data['end'] = {
                'date': data['start']['date'],
                'time': None,
                'note': '',
            }
            data['status'] = self._generate_status(data)
            data['id'] = self._generate_id(data)

            yield data

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

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        return ''

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        # Finds date in format "9-14-2018"
        str_date = re.search(r'\d{1,2}-\d{1,2}-\d{2,4}', item).group(0)
        list_date = str_date.split("-")
        # Zero padding to get into proper format for strptime
        if len(list_date[0]) == 1:
            list_date[0] = "0" + list_date[0]
        if len(list_date[1]) == 1:
            list_date[1] = "0" + list_date[1]
        # Two dates in 2014 have an abbreviated year rather than the full one
        if len(list_date[2]) == 2:
            list_date[2] = "20" + list_date[2]
        formatteddate = "-".join(list_date)
        datetime_item = datetime.strptime(formatteddate, '%m-%d-%Y')
        return {'date': datetime_item.date(), 'time': '', 'note': ''}

    def _parse_location(self, item):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        return {
            'address': '4054 N. Lincoln Avenue',
            'name': 'Northcenter Chamber of Commerce',
            'neighborhood': '',
        }

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """
        if item is not None:
            url = re.search(r'htt.+?">', item).group(0)[:-2]
            return [{'url': url, 'note': 'SSA Commission Meeting Minutes'}]

    def _parse_first(self, item, links):
        next_meeting = None
        pattern = \
            '(January|February|March|April|May|June|July|August|September|October|November|December).+?(th|nd|st|rd)'
        for x in item:
            if re.search(pattern, x):
                # From looking at archived version of the page,
                # I'm only expecting one instance of a month string, and that's for upcoming meetings.
                next_str = re.search(pattern, x).group(0)[:-2]
                # Zero padding if necessary
                if not next_str[-2].isdigit():
                    next_str = next_str[:-1] + '0' + next_str[-1:]
                next_meeting = datetime.strptime(next_str, '%B %d')

        agenda = ''

        for link in links:
            if "Agenda" in link or "agenda" in link:
                agenda = link

        data = None

        if next_meeting is not None:
            data = {
                '_type': 'event',
                'name': self._parse_name(item),
                'event_description': self._parse_description(item),
                'classification': self._parse_classification(item),
                'start': {'date': next_meeting, 'time': None},
                'all_day': False,
                'location': self._parse_location(item),
                'documents': [{'url': agenda, 'note': 'SSA Commission Meeting Agenda'}],
                'sources': [{
                    'url': 'http://www.northcenterchamber.com/pages/MeetingsTransparency1',
                    'note': ''
                }]
            }

            data['end'] = {
                'date': data['start']['date'],
                'time': None,
                'note': '',
            }
            data['status'] = self._generate_status(data)
            data['id'] = self._generate_id(data)

        return data
