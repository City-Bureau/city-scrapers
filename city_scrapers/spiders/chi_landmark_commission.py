import re
from datetime import datetime, time

import dateutil.parser
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiLandmarkCommissionSpider(CityScrapersSpider):
    name = 'chi_landmark_commission'
    agency = 'Commission on Chicago Landmarks'
    timezone = 'America/Chicago'
    allowed_domains = ['www.chicago.gov']
    start_urls = ['https://www.chicago.gov/city/en/depts/dcd/supp_info/landmarks_commission.html']

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        columns = self.parse_meetings(response)
        for column in columns:
            year = column.xpath('preceding::h3[1]/text()').re_first(r'(\d{4})(.*)')
            # meetings usually in table cell but a few are nested under p tags (e.g. Jul. 2014)
            meeting_date_xpath = 'text()[normalize-space()]|p/text()[normalize-space()]'
            meetings = column.xpath(meeting_date_xpath).extract()
            meetings = self.format_meetings(meetings)
            for item in meetings:
                meeting = Meeting(
                    title='Commission',
                    description='',
                    classification=COMMISSION,
                    start=self._parse_start(item, year),
                    end=None,
                    time_notes='',
                    all_day=False,
                    location={
                        'name': 'City Hall',
                        'address': '121 N LaSalle St, Room 201A, Chicago, IL 60602'
                    },
                    source=response.url,
                )
                meeting['links'] = self._parse_links(column, meeting, response)
                meeting['id'] = self._get_id(meeting)
                meeting['status'] = self._get_status(meeting)
                yield meeting

    @staticmethod
    def format_meetings(meetings):
        # translate and filter out non-printable spaces
        meetings = [meeting.replace('\xa0', ' ').strip() for meeting in meetings]
        meetings = list(filter(None, meetings))
        return meetings

    @staticmethod
    def parse_meetings(response):
        meeting_xpath = """
            //td[preceding::h3[1]/text()[
                contains(., "Meeting Schedule")
                ]]"""
        return response.xpath(meeting_xpath)

    @staticmethod
    def _parse_start(meeting, year):
        m = re.search(r'(?P<month>\w+)\.?\s(?P<day>\d+).*', meeting.strip())
        dt = dateutil.parser.parse(m.group('month') + ' ' + m.group('day') + ' ' + year)
        # time based on examining meeting minutes
        return datetime.combine(dt.date(), time(12, 45))

    @staticmethod
    def _parse_links(item, data, response):
        month = data['start'].strftime("%B")
        xp = './/a[contains(@title, "{0}")]'.format(month)
        documents = item.xpath(xp)
        if len(documents) >= 0:
            return [{
                'href': response.urljoin(document.xpath('@href').extract_first()),
                'title': document.xpath('text()').extract_first()
            } for document in documents]
        return []
