# -*- coding: utf-8 -*-

from datetime import datetime

from documenters_aggregator.spider import Spider


class Cook_hospitalsSpider(Spider):
    name = 'cook_hospitals'
    long_name = 'Cook County Health and Hospitals System'
    allowed_domains = ['www.cookcountyhhs.org']
    start_urls = ['http://www.cookcountyhhs.org/about-cchhs/governance/board-committee-meetings/']
    domain_root = 'http://www.cookcountyhhs.org'

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.
        """
        for item in response.xpath("//a[@class='h2 accordion-toggle collapsed']"):
            data = {
                '_type': 'event',
                'name': self._parse_name(item),
                'end_time': self._parse_end(item),
                'all_day': self._parse_all_day(item),
                'sources': self._parse_sources(response),
                'timezone': 'America/Chicago'
            }

            aria_control = item.xpath("@aria-controls").extract_first()
            item_uncollapsed = item.xpath("//div[@id='{}']//tbody//td[@data-title='Meeting Information']".format(aria_control))
            for subitem in item_uncollapsed:
                new_item = {
                    'description': self._parse_description(subitem),
                    'classification': self._parse_classification(subitem),
                    'start_time': self._parse_start(subitem),
                    'location': self._parse_location(subitem)
                }
                new_item.update(data)
                new_item['status'] = self._parse_status(subitem, new_item['start_time'])
                new_item['id'] = self._generate_id(data, new_item['start_time'])
                yield new_item

    def _parse_classification(self, item):
        """
        @TODO Not implemented
        """
        return 'Not classified'

    def _parse_status(self, subitem, start_time):
        """
        @TODO
        passed = meeting already started
        tentative = no agenda posted
        confirmed = agenda posted
        Is this the right way to determine tentative vs confirmed?
        Looks like agendas are usually posted a week before the meeting
        """
        if datetime.now().isoformat() > start_time.isoformat():
            return 'passed'
        agenda = subitem.xpath("following-sibling::td/a/@href").extract_first()
        if agenda is None:
            return 'tentative'
        else:
            return 'confirmed'

    def _parse_location(self, subitem):
        """
        Parse location
        """
        return {
            'url': '',
            'name': '',
            'address': subitem.xpath('text()').extract()[1].strip(),
            'coordinates': {'longitude': '', 'latitude': ''},
        }

    def _parse_all_day(self, item):
        """
        It appears all events have a start and end time on the CCHHS website,
        so this `all_day` is always false.
        """
        return False

    def _parse_name(self, item):
        """
        Get event name from item's text
        """
        return item.xpath('text()').extract_first().strip()

    def _parse_description(self, subitem):
        """
        Get url to agenda
        """
        return ("The CCHHS is charged with delivering integrated health services with "
                "dignity and respect regardless of a patient’s ability to pay; "
                "fostering partnerships with other health providers and communities "
                "to enhance the health of the public; and advocating for policies "
                "that promote the physical, mental and social well being of the people of Cook County. " 
                "The CCHHS Board of Directors has five standing committees.")

    def _parse_start(self, subitem):
        """
        Combine start time with year, month, and day.
        """
        start_time = subitem.xpath('text()').extract()[0].strip()
        return self._make_date(start_time)

    def _parse_end(self, item):
        """
        End times vary depending on the agenda
        """
        return None

    def _make_date(self, start_time):
        """
        Combine year, month, day with variable time and export as timezone-aware,
        ISO-formatted string.
        """

        start_split = start_time.split(' ')
        month = start_split[0]
        day = start_split[1].replace(',', '').zfill(2)
        year = start_split[2]
        time = start_split[4].zfill(5)
        am_pm = start_split[5]

        fmt_string = '{year} {month} {day} {time}{am_pm}'
        time_string = fmt_string.format(year=year, month=month, day=day, time=time, am_pm=am_pm)

        naive = datetime.strptime(time_string, '%Y %B %d %I:%M%p')
        return self._naive_datetime_to_tz(naive)

    def _parse_sources(self, response):
        """
        Parse sources.
        """
        return [{'url': response.url, 'note': ''}]
