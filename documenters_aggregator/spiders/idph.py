# -*- coding: utf-8 -*-
import scrapy


class IdphSpider(scrapy.Spider):
    name = 'idph'
    allowed_domains = ['www.dph.illinois.gov']
    start_urls = ['http://www.dph.illinois.gov/events']

    def parse(self, response):
        return {
            'key': 'key',
            'value': 'value',
        }
