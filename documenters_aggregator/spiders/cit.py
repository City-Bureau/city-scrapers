# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy, re, datetime as dt, pytz


class CitSpider(scrapy.Spider):
    name = 'cit'
    allowed_domains = ['chicagoinfrastructure.org']
    start_urls = ['http://chicagoinfrastructure.org/public-records/scheduled-meetings/']

    year = dt.date.today().year

    def parse(self, response):
        """
        Currently, the meeting page just gives dates, so there's limited info to report.
        The dates have no years, but the list has a year at the top. I pull this
        to add to the datetimes.
        """

        year_item = response.css('div.entry')[1].css('div.entry p')[0].extract()
        year_match = re.search(r'([0-9]{4})', year_item)
        self.year = int(year_match.group(1))

        for item in response.css('div.entry')[1].css('div.entry p')[1:]:
            yield {
                '_type': 'event',
                'id': self._parse_id(item),
                'name': 'Chicago Infrastructure Trust',
                'description': None,
                'classification': 'Board Meeting',
                'start_time': self._parse_start(item),
                'end_time': None,
                'all_day': False,
                'status': 'tentative',
                'location': None,
            }


        # self._parse_next(response) yields more responses to parse if necessary.
        # uncomment to find a "next" url
        # yield self._parse_next(response)

    # def _parse_next(self, response):
    #     """
    #     Get next page. You must add logic to `next_url` and
    #     return a scrapy request.
    #     """
    #     next_url = None  # What is next URL?
    #     return scrapy.Request(next_url, callback=self.parse)

    def _parse_id(self, item):
        """
        Returns date string for unique ID
        """
        extracted = item.extract()
        match = re.search(r'([a-zA-Z]*),\s{1}([a-zA-Z]+)\s([0-9]{1,2})', extracted)

        start_date_obj = dt.datetime.strptime(match.group(0), "%A, %B %d")
        start_date = start_date_obj.replace(year = self.year)
        id_date = start_date.date().isoformat()
        return id_date

    # def _parse_classification(self, item):
    #     """
    #     Parse or generate classification (e.g. town hall).
    #     """
    #     return 'Not classified'

    # def _parse_status(self, item):
    #     """
    #     Parse or generate status of meeting. Can be one of:

    #     * cancelled
    #     * tentative
    #     * confirmed
    #     * passed

    #     By default, return "tentative"
    #     """
    #     return 'tentative'

    # def _parse_location(self, item):
    #     """
    #     Parse or generate location. Url, latitutde and longitude are all
    #     optional and may be more trouble than they're worth to collect.
    #     """
    #     return {
    #         'url': None,
    #         'name': None,
    #         'coordinates': {
    #           'latitude': None,
    #           'longitude': None,
    #         },
    #     }

    # def _parse_all_day(self, item):
    #     """
    #     Parse or generate all-day status. Defaults to false.
    #     """
    #     return False

    # def _parse_name(self, item):
    #     """
    #     Parse or generate event name.
    #     """
    #     return None

    # def _parse_description(self, item):
    #     """
    #     Parse or generate event name.
    #     """
    #     return None

    def _parse_start(self, item):
        """
        No times given; set to Midnight
        """
        extracted = item.extract()
        match = re.search(r'([a-zA-Z]*),\s{1}([a-zA-Z]+)\s([0-9]{1,2})', extracted)

        start_date_obj = dt.datetime.strptime(match.group(0), "%A, %B %d")
        start_date = pytz.timezone('US/Central').localize(start_date_obj)
        start_date = start_date.astimezone(pytz.utc)
        start_date = start_date.replace(year = self.year,
                                                   hour = 0,
                                                   minute = 0)
        start_date_str = start_date.isoformat()

        return start_date_str

    # def _parse_end(self, item):
    #     """
    #     Parse end date and time.
    #     """
    #     return None
