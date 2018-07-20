# -*- coding: utf-8 -*-
import scrapy
from city_scrapers.spider import Spider
from datetime import datetime


class Chi_teacherpensionSpider(Spider):
    name = 'chi_teacherpension'
    agency_id = 'Chicago Teachers Pension Fund'
    timezone = 'America/Chicago'
    allowed_domains = ['www.ctpf.org']
    start_urls = ['https://www.ctpf.org/post/board-meetings']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        
        for i in range(1,4): 

            dates = self.get_dates(response, i)
            for date in dates:

                data = {
                            '_type': 'event',
                            'name': self._parse_name(response, i),
                            'description': self._parse_description(response, i),
                            'classification': self._parse_classification(i),
                            'start': self._parse_start(response, date, i),
                            'end': self._parse_end(date),
                            'status': self._parse_status(),
                            'all_day': self._parse_all_day(),
                            'location': self._parse_location(),
                            'sources': self._parse_sources(response),
                        }

                data['id'] = self._generate_id(data)

                yield data


    def get_dates(self, response, i):
        if i == 1:
            raw = response.xpath('//*[@id="node-full"]/div/div[2]/h3[1]/following-sibling::p[1]/text()').extract()
        else:
            raw = response.xpath('//*[@id="node-full"]/div/div[2]/h3['+str(i)+']/following-sibling::p[2]/text()').extract()
        
        return [date.strip() for date in raw]

    def _parse_name(self, response, i):
        """
        Parse or generate event name.
        """
        cut = len(' Schedule')

        if i == 3:
        	name = response.xpath('//*[@id="node-full"]/div/div[2]/h4[1]/text()').extract_first()
        else:
        	name = response.xpath('//*[@id="node-full"]/div/div[2]/h3['+str(i)+']/text()').extract_first()
        
        return name[0:len(name)-cut]

    def _parse_description(self, response, i):
        """
        Parse or generate event description.
        """
        if i == 1:
        	return response.xpath('//*[@id="node-full"]/div/div[2]/p[1]/text()').extract_first()
        elif i ==2:
        	return response.xpath('//*[@id="node-full"]/div/div[2]/p[3]/text()').extract_first()
        else:
        	return response.xpath('//*[@id="node-full"]/div/div[2]/p[5]/text()').extract_first()
        

    def _parse_classification(self, i):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        if i == 1:
        	return 'board meeting'
        else:
        	return 'committee meeting'

    def _parse_start(self, response, date, i):
        """
        Parse start date and time.
        """
        date = datetime.strptime(date, '%A, %B %d, %Y')
        
        if i ==3:
        	time = None
        	note = response.xpath('//*[@id="node-full"]/div/div[2]/p[5]/text()').extract_first()
        else:
        	time = datetime.strptime('9:30am', '%H:%M%p').time()
        	note = ''
        
        return {
                    'date': date,
                    'time': time,
                    'note': note
                }


    def _parse_end(self, date):
        """
        Parse end date and time.
        """
        date = datetime.strptime(date, '%A, %B %d, %Y')

        return {
                    'date': date,
                    'time': None,
                    'note': ''
                }

    def _parse_all_day(self):
        """
        Parse or generate all-day status. Defaults to False.
        """
        return False

    def _parse_location(self):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        return {
            'address': '203 North LaSalle Street, Suite 2600, Board Room',
            'name': 'CTPF office',
            'neighborhood': 'Loop'
        }

    def _parse_status(self):
        """
        Parse or generate status of meeting. Can be one of:
        * cancelled
        * tentative
        * confirmed
        * passed
        By default, return "tentative"
        """
        return 'tentative'

    def _parse_sources(self, response):
        """
        Parse or generate sources.
        """
        return [{
            'url': response.url,
            'note': ''
        }]

