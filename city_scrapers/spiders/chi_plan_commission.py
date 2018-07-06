# -*- coding: utf-8 -*-
from datetime import datetime, time

import scrapy
from city_scrapers.spider import Spider


class Chi_plan_commissionSpider(Spider):
    name = 'chi_plan_commission'
    long_name = 'Chicago Plan Commission'
    allowed_domains = ['www.cityofchicago.org']
    start_urls = ['https://www.cityofchicago.org/city/en/depts/dcd/supp_info/chicago_plan_commission.html']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        items = self.parse_meetings(response)
        desc_xpath = '//p[contains(text(), "The Chicago Plan Commission")]/text()'
        description = response.xpath(desc_xpath).extract_first(default='').strip()
        for item in items:
            data = {
                '_type': 'event',
                'name': 'Chicago Plan Commission',
                'event_description': description,
                'classification': 'Commission',
                'start': self._parse_start(item),
                # Based on meeting minutes, board meetings appear to be all day
                'all_day': True,
                'location': {'neighborhood': '',
                             'name': 'City Hall',
                             'address': '121 N. LaSalle St., in City Council chambers'},
                'sources': [{'url': response.url, 'note': ''}],
                'documents': self._parse_documents(item, response),
            }

            data['end'] = {'date': data['start']['date'], 'time': None, 'note': ''}
            data['id'] = self._generate_id(data)
            data['status'] = self._generate_status(data, '')
            yield data

    def parse_meetings(self, response):
        meeting_xpath = """
        //td[contains(text(), "January") or
             contains(text(), "February") or
             contains(text(), "March") or
             contains(text(), "April") or
             contains(text(), "May") or
             contains(text(), "June") or
             contains(text(), "July") or
             contains(text(), "August") or
             contains(text(), "September") or
             contains(text(), "October") or
             contains(text(), "November") or
             contains(text(), "December") 
        ]"""
        return response.xpath(meeting_xpath)

    def _parse_start(self, item):
        year = item.xpath('preceding::strong[1]/text()').re_first(r'(\d{4})(.*)')
        month, day = item.xpath('text()[following-sibling::br[not(preceding-sibling::br)]][1]').re(r'(\w+)\s(\d+).*')
        dt = datetime.strptime(month + ' ' + day + ' ' + year, '%B %d %Y')
        # time based on examining meeting minutes
        return {'date': dt.date(), 'time': time(10, 0), 'note': ''}

    def _parse_documents(self, item, response):
        documents = item.xpath('a[following-sibling::br[not (preceding-sibling::br)]]')
        return [{'url': response.urljoin(document.xpath('@href').extract_first()),
                 'note': document.xpath('text()').extract_first()}
                for document in documents]