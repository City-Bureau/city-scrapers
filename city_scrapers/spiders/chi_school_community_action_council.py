# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta, time

from city_scrapers.constants import COMMITTEE
from city_scrapers.spider import Spider


class ChiSchoolCommunityActionCouncilSpider(Spider):
    name = 'chi_school_community_action_council'
    agency_name = 'Chicago Public Schools'
    timezone = 'America/Chicago'
    allowed_domains = ['cps.edu']
    start_urls = ['http://cps.edu/FACE/Pages/CAC.aspx']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        # Sets month counter to the current month, passed to parse_start
        month_counter = datetime.today().month
        # Iterates through every month in the year after the current month
        for x in range(12):
            if month_counter > 12:
                break
            else:
                response_list = response.css('.ms-WPBody ul:last-of-type')
                for item in response_list.css('li'):
                    name_link = item.css('strong').css('a::attr(href)')
                    try:
                        if name_link.extract()[0] == (
                            'http://www.humboldtparkportal.org/'
                        ):
                            continue
                    except:
                        pass
                    data = {
                        '_type': 'event',
                        'name': self._parse_name(item),
                        'event_description': '',
                        'classification': COMMITTEE,
                        'start': self._parse_start(item, month_counter),
                        'all_day': False,
                        'location': self._parse_location(item),
                        'sources': self._parse_sources(response, item),
                        'documents': [],
                    }

                    data['id'] = self._generate_id(data)
                    data['status'] = self._generate_status(data, text='')
                    data['end'] = self._parse_end(data['start'])
                    yield data
            month_counter += 1

    def _parse_community_area(self, item):
        """
        Parse or generate community area.
        """
        if len(item.css('li').css('strong::text').extract()) == 1:
            community_name = item.css('li').css('strong::text').extract()
        else:
            community_name = item.css('li').css(
                'strong').css('a::text').extract()
        if len(community_name) > 0:
            return community_name[0]

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        CAC_NAME = 'Community Action Council'
        community_area = self._parse_community_area(item)
        if community_area:
            return f'{community_area} {CAC_NAME}'
        return CAC_NAME

    @staticmethod
    def parse_day(source):
        """
        Parses the source material and retrieves the day of the week that
        the meeting occurs.
        """
        day_source = source[0]
        day_regex = re.compile(r'[a-zA-Z]+day')
        mo = day_regex.search(day_source)
        return mo.group().lower()

    @staticmethod
    def parse_time(source):
        """
        Parses the source material and retrieves the time that the meeting
        occurs.
        """
        time_source = source[1]
        time_regex = re.compile(r'(1[012]|[1-9]):([0-5][0-9])(am|pm)')
        hour, minute, period = time_regex.search(time_source).groups()
        hour = int(hour)
        minute = int(minute)
        if (period == 'pm') and (hour != 12):
            hour += 12
        return time(hour, minute)

    @staticmethod
    def count_days(day, week_count, month_counter):
        """
        Because the source material provides meeting dates on a reoccuring
        schedule, we must use the parsed day from the parse_day function
        """
        today = datetime.today()
        week_day = {
            'monday': 0,
            'tuesday': 1,
            'wednesday': 2,
            'thursday': 3,
            'friday': 4,
            'saturday': 5,
            'sunday': 6,
        }
        week_counter = 0
        for x in range(1, 31):
            try:
                current_date = datetime(today.year, month_counter, x)
                if current_date.weekday() == week_day[day]:
                    week_counter += 1
                    if week_counter == int(week_count):
                        return current_date
            except ValueError as e:
                break

    def _parse_start(self, item, month_counter):
        """
        Parse start date and time.
        Accepts month_counter as an argument from top level parse function
        to iterate through all months in the year.
        """
        source = item.css('li::text').extract()
        day = self.parse_day(source)
        # Selects first character in the source, usually the week count
        week_count = source[0].strip()[0]
        if week_count.isdigit():
            meeting_date = self.count_days(day, week_count, month_counter)
            return {
                'date': meeting_date.date(),
                'time': self.parse_time(source),
                'note': ''
            }
        return {
            'date': None,
            'time': None,
            'note': ''
        }

    def _parse_end(self, start):
        """
        Estimates the end time by adding 3 hours to the start time.
        """
        try:
            start_datetime = datetime.combine(start['date'], start['time'])
        except TypeError: 
            # start date or time is None
            return {
                'date': start['date'],
                'time': None,
                'note': 'No start or end time available'
            }
        else:
            end_datetime = start_datetime + timedelta(hours=3)
            return {
                'date': end_datetime.date(),
                'time': end_datetime.time(),
                'note': 'Estimated 3 hours after the start time'
            }

    def _parse_location(self, item):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        source = item.css('li::text').extract()[1]
        address = source[source.find("(") + 1:source.find(")")]
        return {
            'name': source[
                source.find('at') + 2:source.find('(')
            ].replace('the', '').strip(),
            'address': '{} Chicago, IL'.format(address),
            'neighborhood': self._parse_community_area(item)
        }

    def _parse_sources(self, response, item):
        """
        Parse the sources:
        * CAC Meetings Website
        * Neighborhood Website (if available)
        """
        sources = [{
            'url': response.url,
            'note': 'CAC Meetings Website',
        }]
        neighborhood_url = item.css('li').css('strong').css(
            'a::attr(href)').extract_first()
        if neighborhood_url:
            sources.append({
                'url': neighborhood_url,
                'note': "Neighborhood's Website"
            })
        return sources
