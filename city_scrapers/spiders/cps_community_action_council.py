# -*- coding: utf-8 -*-
import scrapy
from city_scrapers.spider import Spider
from datetime import datetime
from dateutil.parser import parse as dateparse
import re

class Cps_community_action_councilSpider(Spider):
    name = 'cps_community_action_council'
    long_name = 'CPS Community Action Council'
    allowed_domains = ['cps.edu']
    start_urls = ['http://cps.edu/FACE/Pages/CAC.aspx']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css("ul").css('li')[17:]:

            data = {
                '_type': 'event',
                'id': self._parse_id(item),
                'name': self._parse_name(item),
                'description': self._parse_description(item),
                'classification': self._parse_classification(item),
                'start_time': self._parse_start(item),
                'end_time': self._parse_end(item),
                'timezone': self._parse_timezone(item),
                'status': self._parse_status(item),
                'all_day': self._parse_all_day(item),
                'location': self._parse_location(item),
                'sources': self._parse_sources(item),
            }

            data['id'] = self._generate_id(data, data['start_time'])
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

    def _parse_id(self, item):
        """
        Calulate ID. ID must be unique and in the following format:
        <spider-name>/<start-time-in-YYYYMMddhhmm>/<unique-identifier>/<underscored-event-name>

        Example:
        chi_buildings/201710161230/2176/daley_plaza_italian_exhibit
        """
        return ''

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        if len(item.css('li').css('strong::text').extract()) == 1:
            community_name = item.css('li').css('strong::text').extract()
        else:
            community_name = item.css('li').css('strong').css('a::text').extract()
        name = community_name[0] + ' community action council meeting'
        return name

    def _parse_description(self, item):
        """
        Parse or generate event description.
        """
        return ''

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        return 'Not classified'

    def _parse_start(self, item):
        """
        Parse start date and time.
        """

        def parse_day(source):
            '''Parses the source material and retrieves the day of the week that the meeting occurs.
            '''
            day_source = source[0]
            day_regex = re.compile(r'[a-zA-Z]+day')
            mo = day_regex.search(day_source)
            return mo.group().lower()

        def parse_time(source):
            '''Parses the source material and retrieves the time that the meeting occurs.
            '''
            time_source = source[1]
            time_regex = re.compile(r'(1[012]|[1-9]):[0-5][0-9](am|pm)')
            mo = time_regex.search(time_source)
            return mo.group()

        def count_days(day, week_count):
            '''Because the source material provides meeting dates on a reoccuring schedule, we must use the parsed day
            from the parse_day function and the '''
            today = datetime.today()
            week_day = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3, 'friday': 4, 'saturday': 5,
                        'sunday': 6}
            week_counter = 0
            for x in range(1, 31):
                try:
                    current_date = datetime(today.year, today.month, x)
                    if current_date.weekday() == week_day[day]:
                        week_counter += 1
                        if week_counter == int(week_count):
                            return current_date
                except ValueError as e:  # will break loop if range exceeds the number of days in the month
                    break

        def concat_date(meeting_date, time):
            '''Combines the meeting date with the time the meeting occurs. Function return a datetime
            object.
            '''
            return dateparse(
                str(meeting_date.year) + '-' + str(meeting_date.month) + '-' + str(meeting_date.day) + ' ' + time)


        source = item.css('li::text').extract()
        try:
            day = parse_day(source)
            week_count = source[0].strip()[0]  # selects first character in the source, which is usually the week count
            if week_count.isdigit():
                time = parse_time(source)
                meeting_date = count_days(day, week_count)
                output = concat_date(meeting_date, time)
            else:
                pass
        except (AttributeError) as e:
            output = datetime(1970, 1, 1)
        return output

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        return ''

    def _parse_timezone(self, item):
        """
        Parse or generate timzone in tzinfo format.
        """
        return 'America/Chicago'

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to False.
        """
        return False

    def _parse_location(self, item):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        return {
            'url': '',
            'name': '',
            'address': '',
            'coordinates': {
                'latitude': '',
                'longitude': '',
            },
        }

    def _parse_status(self, item):
        """
        Parse or generate status of meeting. Can be one of:
        * cancelled
        * tentative
        * confirmed
        * passed
        By default, return "tentative"
        """
        return 'tentative'

    def _parse_sources(self, item):
        """
        Parse or generate sources.
        """
        return [{
            'url': '',
            'note': '',
        }]