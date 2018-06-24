# -*- coding: utf-8 -*-
import scrapy
from city_scrapers.spider import Spider
from datetime import datetime


class Chi_teacherpensionSpider(Spider):
    name = 'chi_teacherpension'
    long_name = 'Chicago Teachers Pension Fund'
    allowed_domains = ['www.ctpf.org']
    start_urls = ['http://www.ctpf.org/general_info/boardmeetings.htm']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for i in range(1,len(response.xpath('//*[@id="content"]/h4[4]/preceding-sibling::p').extract())+1):
            data = {
                        '_type': 'event',
                        'id': self._parse_id(item),
                        #'name': self._parse_name(item),
                        'description': self._parse_description(item),
                        'classification': self._parse_classification(item),
                        #'start_time': self._parse_start(item),
                        'end_time': self._parse_end(item),
                        'timezone': self._parse_timezone(item),
                        'status': self._parse_status(item),
                        'all_day': self._parse_all_day(item),
                        'location': self._parse_location(item),
                        'sources': self._parse_sources(item),
                    }


            x = '//*[@id="content"]/p['+str(i)+']/preceding-sibling::h4/div/text()'
            title = response.xpath(x).extract()[-1]
            date = response.xpath('//*[@id="content"]/p['+str(i)+']/text()').extract()
            if len(date)>0:
                date = re.findall(r'[A-Za-z]+ [0-9]+, [0-9]+',date[0])
                if len(date)>0:
                    data['name'] = title
                    if title in ['Regular Meeting Schedule', 'Investments Committee Meeting Schedule']:
                        date_time = date+' 9:30am'
                    else:
                        # After noon, will address better later
                        date_time = date+' 12:00am'
                    data['start_time'] = self._parse_start(date_time)

                    '''
                    data = {
                        '_type': 'event',
                        'id': self._parse_id(item),
                        #'name': self._parse_name(item),
                        'description': self._parse_description(item),
                        'classification': self._parse_classification(item),
                        #'start_time': self._parse_start(item),
                        'end_time': self._parse_end(item),
                        'timezone': self._parse_timezone(item),
                        'status': self._parse_status(item),
                        'all_day': self._parse_all_day(item),
                        'location': self._parse_location(item),
                        'sources': self._parse_sources(item),
                    }
                    '''

                data['id'] = self._generate_id(data, start_time)

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

    def _parse_start(self, date_time):
        """
        Parse start date and time.
        """
        return datetime.strptime(date_time, '%B %d, %Y %H:%M%p')

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
            'address': '203 North LaSalle Street, Suite 2600, Board Room',
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