# -*- coding: utf-8 -*-
import scrapy
from city_scrapers.spider import Spider
from datetime import datetime, timedelta, time
from dateutil.parser import parse as dateparse
import re

class Chi_school_community_action_councilSpider(Spider):
    name = 'chi_school_community_action_council'
    agency_id = 'Chicago Public Schools Community Action Councils'
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
                        'event_description': self._parse_description(),
                        'classification': self._parse_classification(),
                        'start': self._parse_start(item, month_counter),
                        'all_day': self._parse_all_day(item),
                        'location': self._parse_location(item),
                        'sources': self._parse_sources(response, item),
                        'documents': self._parse_documents()
                    }

                    data['id'] = self._generate_id(data)
                    data['status'] = self._generate_status(data, text='')
                    data['end'] = self._parse_end(data['start'])
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

    def _parse_description(self):
        """
        Parse or generate event description.
        """
        return ''

    def _parse_classification(self):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        return 'committee'

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
            time_regex = re.compile(r'(1[012]|[1-9]):([0-5][0-9])(am|pm)')
            hour, minute, period = time_regex.search(time_source).groups()
            hour = int(hour)
            minute = int(minute)
            if (period == 'pm') and (hour != 12):
                hour += 12
            return time(hour, minute)

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

        def get_start(source):
            '''Combines above defined parse_day, parse_time, count_days, and concat_date functions to get the start
             date from the source. If a start time cannot be found the UNIX epoch date is returned.
             '''
            day = parse_day(source)
            week_count = source[0].strip()[
                0]  # selects first character in the source, which is usually the week count
            if week_count.isdigit():
                meeting_date = count_days(day, week_count)
                return {
                    'date': meeting_date.date(),
                    'time': parse_time(source),
                    'note': ''
                }
            return {
                'date': None,
                'time': None,
                'note': ''
            }

        source = item.css('li::text').extract()

        return get_start(source)

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
            'name': source[source.find("at")+2:source.find("(")].replace('the', ''),
            'address': source[source.find("(")+1:source.find(")")],
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
        neighborhood_url = item.css('li').css('strong').css('a::attr(href)') \
                               .extract_first()
        if neighborhood_url:
            sources.append({
                'url': neighborhood_url,
                'note': "Neighborhood's Website"
            })
        return sources

    def _parse_documents(self):
        """
        No documents on the site
        """
        return []