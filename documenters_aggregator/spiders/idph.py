# -*- coding: utf-8 -*-
import scrapy


class IdphSpider(scrapy.Spider):
    name = 'idph'
    allowed_domains = ['www.dph.illinois.gov']
    start_urls = ['http://www.dph.illinois.gov/events']
    domain_root = 'http://www.dph.illinois.gov'

    def parse(self, response):
        for item in response.css('.eventspage'):
            # @TODO factor into self._parse_item()
            title = item.css('div.eventtitle::text').extract()
            description = ''.join(item.css('div.event_description p::text').extract())
            yield {
                'title': title,
                'description': description,
            }

        # @TODO factor into self._get_next
        next_url = response.css('.pager-next a::attr(href)').extract_first()
        next_url = '{0}{1}'.format(self.domain_root, next_url)
        yield scrapy.Request(next_url, callback=self.parse)
