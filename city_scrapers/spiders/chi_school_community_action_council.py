# -*- coding: utf-8 -*-
import scrapy
from city_scrapers.spider import Spider
from datetime import datetime, timedelta
from dateutil.parser import parse as dateparse
import re

class chi_school_community_action_councilSpider(Spider):
    name = 'chi_school_community_action_council'
    long_name = 'Chicago Public Schools Community Action Council'
    allowed_domains = ['cps.edu']
    start_urls = ['http://cps.edu/FACE/Pages/CAC.aspx']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        month_counter = datetime.today().month # Sets month counter to the current month, which is passed to parse_start
        for x in range(12): # iterates through every month in the year after the current month
            if month_counter > 12:
                break
            else:
                for item in response.css("ul").css('li')[17:]:
                    try:
                        if item.css("strong").css("a::attr(href)").extract()[0] == 'http://www.humboldtparkportal.org/':
                            continue
                    except:
                        pass

                    data = {
                        '_type': 'event',
                        'name': self._parse_name(item),
                        'description': self._parse_description(item),
                        'classification': self._parse_classification(item),
                        'start_time': self._parse_start(item, month_counter),
                        'end_time': self._parse_end(item),
                        'timezone': self._parse_timezone(item),
                        'status': self._parse_status(item),
                        'all_day': self._parse_all_day(item),
                        'location': self._parse_location(item),
                        'sources': self._parse_sources(response),
                        'community_area' : self._parse_community_area(item)
                    }

                    data['id'] = self._generate_id(data, data['start_time'])
                    data['end_time'] = data['start_time'] + timedelta(hours=3) #adds 3 hours to start time
                    yield data
            month_counter += 1  # month counter is increased by 1 month with each iteration of the for loop

    # self._parse_next(response) yields more responses to parse if necessary.
    # uncomment to find a "next" url
    # yield self._parse_next(response)

    def _parse_community_area(self, item):
        """
        Parse or generate community area.
        """
        if len(item.css('li').css('strong::text').extract()) == 1:
            community_name = item.css('li').css('strong::text').extract()
        else:
            community_name = item.css('li').css('strong').css('a::text').extract()
        return community_name[0]

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        if len(item.css('li').css('strong::text').extract()) == 1:
            community_name = item.css('li').css('strong::text').extract()
        else:
            community_name = item.css('li').css('strong').css('a::text').extract()
        return community_name[0] + ' Community Action Council'

    def _parse_description(self, item):
        """
        Parse or generate event description.
        """
        return "Community Action Councils, or CACs, consist of 25-30 voting members who are " \
                                  "directly involved in developing a strategic plan for educational success within " \
                                  "their communities. CAC members include parents; elected officials; faith-based " \
                                  "institutions, health care and community-based organizations; Local School" \
                                  " Council (LSC) members; business leaders; educators and school administrators; " \
                                  "staff members from Chicago's Sister Agencies; community residents; " \
                                  "and students. There are nine CACs across Chicago. Each works to empower the " \
                                  "community they serve to lead the improvement of local quality education."

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        return 'Education'

    def _parse_start(self, item, month_counter):
        """
        Parse start date and time.

        Accepts month_counter as an argument from top level parse function to iterate through all months in the year.
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
                    current_date = datetime(today.year, month_counter, x) #uses month counter from top level parse func.
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

        def get_start(source):
            '''Combines above defined parse_day, parse_time, count_days, and concat_date functions to get the start
             date from the source. If a start time cannot be found the UNIX epoch date is returned.
             '''
            day = parse_day(source)
            week_count = source[0].strip()[
                0]  # selects first character in the source, which is usually the week count
            if week_count.isdigit():
                time = parse_time(source)
                meeting_date = count_days(day, week_count)
                start = concat_date(meeting_date, time)
            else:
                pass
            return start

        source = item.css('li::text').extract()

        return get_start(source)

    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        return 'Estimated 3 hours'

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
        source = item.css('li::text').extract()[1]
        return {
            'url': None,
            'name': source[source.find("at")+2:source.find("(")].replace('the', ''),
            'address': source[source.find("(")+1:source.find(")")],
            'coordinates': {
                'latitude': None,
                'longitude': None,
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
        return 'Tentative'

    def _parse_sources(self, response):
        """
        Parse or generate sources.
        """
        return [{
            'url': response.url,
            'note': '',
        }]
