# -*- coding: utf-8 -*-
import scrapy

from datetime import datetime
from pytz import timezone

class IdphSpider(scrapy.Spider):
    name = 'idph'
    allowed_domains = ['www.dph.illinois.gov']
    start_urls = ['http://www.dph.illinois.gov/events']
    domain_root = 'http://www.dph.illinois.gov'

    def parse(self, response):
        for item in response.css('.eventspage'):
            yield {
                '_type': 'event',
                'id': self._get_event_id(item),
                'name': self._get_event_name(item),
                'description': self._get_event_description(item),
                'classification': 'TK TK',
                'start_time': self._get_event_start(item),
                'end_time': self._get_event_end(item),
                'all_day': False,
                'status': 'tentative',
                'location': {
                    'url': '',
                    'name': 'See description',
                    'coordinates': None,
                },
        }
        yield self._get_next(response)

    def _get_next(self, response):
        """
        Get next page.
        """
        next_url = response.css('.pager-next a::attr(href)').extract_first()
        next_url = '{0}{1}'.format(self.domain_root, next_url)
        return scrapy.Request(next_url, callback=self.parse)

    def _get_event_id(self, item):
        """
        Getting the internal ID is ugly. We need to grab a string like
        "addtocal_node_16206" and grab only the end.
        """
        raw_id_string = item.css('div.addtocal::attr(id)').extract_first()
        return raw_id_string.split('_')[-1]

    def _get_event_name(self, item):
        """
        Get event name from `div.eventtitle`'
        """
        return item.css('div.eventtitle::text').extract_first()

    def _get_event_description(self, item):
        """
        Get event description from `div.event_description`'
        """
        lines = item.css('div.event_description p::text').extract()
        return ''.join(lines)

    def _get_event_start(self, item):
        """
        Combine start time with year, month, and day.
        """
        start_time = item.css('div.start_end_time span::text').extract()[0]
        return self._make_date(item=item, time=start_time)

    def _get_event_end(self, item):
        """
        Combine end time with year, month, and day.
        """
        end_time = item.css('div.start_end_time span::text').extract()[1]
        return self._make_date(item=item, time=end_time)

    def _make_date(self, item, time):
        """
        Combine year, month, day with variable time and export as timezone-aware,
        ISO-formatted string.
        """
        year = datetime.now().year
        month = item.css('div.start_month span::text').extract_first()
        day = item.css('div.start_date_only span::text').extract_first()

        fmt_string = '{year} {month} {day} {time}'
        time_string = fmt_string.format(year=year, month=month, day=day, time=time)

        naive = datetime.strptime(time_string, '%Y %b %d %I:%M%p')

        tz = timezone('America/Chicago')
        return tz.localize(naive).isoformat()
