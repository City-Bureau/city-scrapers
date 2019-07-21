import json
import re
import unicodedata
from datetime import datetime, timedelta

import scrapy
from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class CookLandbankSpider(CityScrapersSpider):
    name = 'cook_landbank'
    agency = 'Cook County Land Bank Authority'
    timezone = 'America/Chicago'

    allowed_domains = ['www.cookcountylandbank.org']
    start_urls = ['http://www.cookcountylandbank.org/wp-admin/admin-ajax.php']
    """
    Set 90 day time horizon
    ie, will poll all dates 45 days before and after today for events.
    """
    time_horizon = 45
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_UP': 1,
    }
    """
    For each date, yields get_events_info which requests info for that
    date with parse() as callback
    """
    def start_requests(self):
        date_stack = self.stack_dates(self.time_horizon)
        for date in date_stack:
            yield self.get_events_info(date)

    def get_events_info(self, date):
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
            callback=self.parse,  # Does this by default, making it explicit
            errback=self.request_err
        )

    def parse(self, response):
        data = json.loads(response.text)
        item = scrapy.Selector(text=data['content'], type="html")

        if not item.css('div.eventon_list_event p.no_events'):
            start = self._parse_start(item)
            location = self._parse_location(item)
            if start is None:
                yield
            title = self._parse_title(item)
            meeting = Meeting(
                title=title,
                description=self._parse_description(item),
                classification=self._parse_classification(title),
                start=start,
                end=None,
                time_notes='',
                all_day=False,
                location=location,
                links=self._parse_links(item),
                source=self._parse_source(item),
            )
            meeting['status'] = self._get_status(meeting)
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def daterange(self, start_date, end_date):
        """Getting dates and setting up AJAX Request"""
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def stack_dates(self, time_horizon):
        today = datetime.now()
        min_date = today - timedelta(days=time_horizon)
        max_date = today + timedelta(days=time_horizon)
        dates = [date for date in self.daterange(min_date, max_date)]
        return dates

    def request_err(self, failure):
        self.logger.error(repr(failure))

    def _parse_id(self, item):
        event_id = item.css('div[data-event_id]::attr(data-event_id)').extract_first()
        return event_id

    def _parse_street_address(self, item):
        street_address = item.css('item [itemprop=\'streetAddress\']::text').extract_first()
        return street_address

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        default_address = '69 W Washington St Chicago, IL 60602'
        street_address = self._parse_street_address(item)
        location_detail = item.css(
            'span[class=\'evcal_desc evo_info \']::attr(data-location_name)'
        ).extract_first()
        if location_detail is not None:
            address = '{}, {}'.format(location_detail, street_address)
        else:
            address = street_address
        if address and 'Chicago' not in address:
            address += ' Chicago, IL'
        return {
            'name': '',
            'address': address or default_address,
        }

    def _parse_title(self, item):
        return item.css('span[class=\'evcal_desc2 evcal_event_title\']::text').extract_first()

    def _parse_description(self, item):
        raw_description = item.xpath('string(normalize-space(//div[@itemprop="description"]))'
                                     ).extract_first()
        normalized_description = unicodedata.normalize("NFKC", raw_description)
        description = re.sub(r'\s+', ' ', normalized_description)

        agenda_sentinal = re.search("agenda", description, re.IGNORECASE)
        if agenda_sentinal:
            description = description[0:agenda_sentinal.start()]

        description = description.strip()

        return description

    @staticmethod
    def _parse_datetime(datetime_str):
        if datetime_str is None:
            return None
        return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')

    def _parse_start(self, item):
        start_date_str = item.css('[itemprop=\'startDate\']::attr(content)').extract_first()
        return self._parse_datetime(start_date_str)

    def _parse_source(self, item):
        return item.css('div[class=\'evo_event_schema\'] a[itemprop=\"url\"]::attr(href)'
                        ).extract_first()

    def _parse_links(self, item):
        documents = []
        item.css('div[itemprop="description"] a')
        for doc_link in item.css('div[itemprop="description"] a'):
            doc_note = doc_link.css('::text').extract_first()
            lower_title = doc_link.attrib['href'].lower()
            if 'click here' in lower_title or 'agenda' in lower_title:
                doc_note = 'Agenda'
            documents.append({
                'href': doc_link.attrib['href'],
                'title': doc_note,
            })
        return documents

    def _parse_classification(self, name):
        if re.search("Board of Directors", name, re.IGNORECASE):
            return BOARD
        else:
            return COMMITTEE
