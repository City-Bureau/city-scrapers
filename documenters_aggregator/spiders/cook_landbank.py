# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy

import json
import datetime as dt

from documenters_aggregator.spider import Spider


class Cook_landbankSpider(Spider):
    """
    Rather than scraping a site, I'm making iterated AJAX requests.
    This means setting up a list of dates to poll for events,
    setting up a dict of data to POST and running parse()
    as a callback on the Response.
    Yields dict for dates with events.
    """
    name = 'cook_landbank'
    long_name = 'Cook County Land Bank'
    allowed_domains = ['www.cookcountylandbank.org']
    start_urls = ['http://www.cookcountylandbank.org/wp-admin/admin-ajax.php']

    """
    Set 90 day time horizon
    ie, will poll all dates 90 days from today for events.
    """
    time_horizon = 90

    """
    A little concerned about getting banned :( so being very conservative; downloading one at a time;
    One second per request. The rest - I believe - is copied from project settings.
    """
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_UP': 1,
        'LOG_ENABLED': True,
        'BOT_NAME': 'documenters_aggregator',
        'COOKIES_ENABLED': False,
        'NEWSPIDER_MODULE': 'documenters_aggregator.spiders',
        'ROBOTSTXT_OBEY': True,
        'SPIDER_MODULES': ['documenters_aggregator.spiders'],
        'USER_AGENT': 'Documenters Aggregator (learn more and say hello at https://TKTK)'
    }

    """
    \/For each date, yields get_events_info which requests info for that date with
    parse() as callback
    """

    def start_requests(self):
        date_stack = self.stack_dates(self.time_horizon)
        for date in date_stack:
            yield self.get_events_info(date)

    def get_events_info(self, date):
        """
        the dict to POST. I copied what was coming from the website. Maybe most is unnecessary?
        """
        request_body = {
            'action': 'the_ajax_hook',
            'current_month': str(date.month),
            'current_year': str(date.year),
            'event_count': '0',
            'fc_focus_day': str(date.day),
            'filters[0][filter_type]': 'tax',
            'filters[0][filter_name]': 'event_type',
            'filters[0][filter_val]': '9, 16, 17, 18, 19, 20, 26, 27',
            'direction': 'none',
            'shortcode[hide_past]': 'no',
            'shortcode[show_et_ft_img]': 'no',
            'shortcode[event_order]': 'DESC',
            'shortcode[ft_event_priority]': 'no',
            'shortcode[lang]': 'L1',
            'shortcode[month_incre]': '0',
            'shortcode[evc_open]': 'no',
            'shortcode[show_limit]': 'no',
            'shortcode[etc_override]': 'no',
            'shortcode[tiles]': 'no',
            'shortcode[tile_height]': '0',
            'shortcode[tile_bg]': '0',
            'shortcode[tile_count]': '2'
        }

        # Making the post request
        return scrapy.FormRequest(
            url=self.start_urls[0],
            formdata=request_body,
            callback=self.parse,  # Does this by default, but making it explicit
            errback=self.request_err
        )

    def parse(self, response):
        data = json.loads(response.text)
        item = scrapy.Selector(text=data['content'], type="html")

        if not item.css('div.eventon_list_event p.no_events'):
            data = {
                '_type': 'event',
                'id': self._parse_id(item),
                'name': self._parse_name(item),
                'description': self._parse_description(item),
                'classification': self._parse_classification(item),
                'start_time': self._parse_start(item),
                'end_time': self._parse_end(item),
                'all_day': self._parse_all_day(item),
                'timezone': 'America/Chicago',
                'status': self._parse_status(item),
                'location': self._parse_location(item),
                'sources': self._parse_sources(item)
            }
            data['id'] = self._generate_id(data, data['start_time'])
            yield data
        else:
            yield

    # Getting dates and setting up AJAX Request

    def daterange(self, start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + dt.timedelta(n)

    def stack_dates(self, time_horizon):
        # min_date = dt.datetime.strptime('2017-09-08', '%Y-%m-%d') # Change in production - just for testing
        min_date = dt.date.today()
        max_date = min_date + dt.timedelta(days=time_horizon)
        dates = [date for date in self.daterange(min_date, max_date)]
        return dates

    def request_err(self, failure):  # If Request throws an error
        self.logger.error(repr(failure))

    # Event element parsers

    def _parse_id(self, item):
        event_id = item.css('div[data-event_id]::attr(data-event_id)').extract_first()
        return event_id

    def _parse_classification(self, item):
        """
        No real 'classification' field to parse
        """
        return 'Not classified'

    def _parse_status(self, item):
        """
        Checks date. Returns 'passed' if before today. Else 'tentative.'
        No other indicator available.
        """
        start_date = item.css('[itemprop=\'startDate\']::attr(datetime)').extract_first()
        if dt.datetime.today() > dt.datetime.strptime(start_date, '%Y-%m-%d'):
            status = 'passed'
        else:
            status = 'tentative'
        return status

    def _parse_street_address(self, item):
        street_address = item.css('item [itemprop=\'streetAddress\']::text').extract_first()
        return street_address

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        street_address = self._parse_street_address(item)
        location_detail = item.css('span[class=\'evcal_desc evo_info \']::attr(data-location_name)').extract_first()
        return {
            'url': 'http://www.cookcountylandbank.org/',
            'name': None,
            'address': location_detail + ", " + street_address,
            'coordinates': {
                'latitude': None,
                'longitude': None,
            },
        }

    def _parse_all_day(self, item):
        """
        No reliable indicator here. Leaving None
        """
        return False

    def _parse_name(self, item):
        name = item.css('span[class=\'evcal_desc2 evcal_event_title\']::text').extract_first()
        return name

    def _parse_description(self, item):
        """
        No real 'description' field to parse. Leaving None.
        """
        return None

    def _parse_start(self, item):
        start_date = item.css('[itemprop=\'startDate\']::attr(datetime)').extract_first()
        start_time = item.css('em.evo_time span[class=\'start\']::text').extract_first()
        start_date_time = dt.datetime.strptime(start_date + ' ' + start_time, '%Y-%m-%d %I:%M %p')
        return self._naive_datetime_to_tz(start_date_time)

    def _parse_end(self, item):
        """
        End date but no end time available. Leaving None.
        Left commented the code to pull the end date if you want to include later.
        """
        # end_date = item.css('[itemprop=\'endDate\']')[0].get('datetime')
        return None

    """
    Was trying to parse the Agenda, but it's pretty irregularly structured.
    The source_url goes straight to all the info and also includes an embedded
    PDF that could potentially be scraped. Didn't bother with that here.
    """
    # def _parse_agenda(self, item):
    #     agenda = []
    #     for item in item.css('div[class=\'eventon_desc_in\'] h4'):
    #     # This captures some, but not all agenda items, because they don't consistently use the same tags
    #     # Not worrying a lot about it now, and it'll be clear in the output that the items numbers are off
    #         description = item.text
    #         if description:
    #             agenda.append(description)
    #         else:
    #             continue
    #     return agenda

    def _parse_sources(self, item):
        source_url = item.css('div[class=\'evo_event_schema\'] a[itemprop=\"url\"]::attr(href)').extract_first()
        return [{
            'url': source_url,
            'note': 'Event Page'
        }]
