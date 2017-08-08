# -*- coding: utf-8 -*-
import scrapy

from datetime import datetime
from pytz import timezone

class CpsboeSpider(scrapy.Spider):
    name = 'cpsboe'
    allowed_domains = ['www.cpsboe.org']
    start_urls = ['http://www.cpsboe.org/meetings/planning-calendar']
    domain_url = 'http://www.cpsboe.org'

    def parse(self, response):
        for item in response.css('#content-primary tr')[1:]:
            yield {
                '_type': 'event',
                'id': self._parse_id(item),
                'name': 'Chicago Board of Education Monthly Meeting',
                'description': self._parse_description(item)
            }

    def _parse_id(self, item):
        """
        Generate an ID by converting the date to an integer.
        i.e. 'July 27, 2016' becomes '20170726'
        """
        text_list = self._remove_line_breaks(item.css('::text').extract())
        split_date_string = text_list[0].split()[:3]
        split_date_string[0] = split_date_string[0][:3]
        split_date_string[1] = split_date_string[1][:-1]
        date_string = " ".join(split_date_string)
        date = datetime.strptime(date_string, '%b %d %Y')
        return str(10000*date.year + 100*date.month + date.day)

    def _remove_line_breaks(self, collection):
        while '\n' in collection: collection.remove("\n")
        return collection

    def _parse_description(self, item):
        """ 
        Currently every description is the same, but it's
        unsafe to assume that will always be the case so let's
        grab it programmatically anyways.
        """
        text_list = self._remove_line_breaks(item.css('td')[1].css('::text').extract())
        description = "\n".join(text_list)
        return description


