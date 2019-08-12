import re
from datetime import datetime, time

import dateutil.parser
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiPlanCommissionSpider(CityScrapersSpider):
    name = 'chi_plan_commission'
    agency = 'Chicago Plan Commission'
    timezone = 'America/Chicago'
    allowed_domains = ['chicago.gov']
    start_urls = ['https://chicago.gov/city/en/depts/dcd/supp_info/chicago_plan_commission.html']

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        columns = self.parse_meetings(response)
        for column in columns:
            year = column.xpath('preceding::strong[1]/text()').re_first(r'(\d{4})(.*)')
            meetings = column.xpath('text()[normalize-space()]|p/text()[normalize-space()]'
                                    ).extract()
            meetings = self.format_meetings(meetings)
            for meeting in meetings:
                start = self._parse_start(meeting, year)
                if start is None:
                    continue
                meeting = Meeting(
                    title='Commission',
                    description='',
                    classification=COMMISSION,
                    start=start,
                    end=None,
                    time_notes='',
                    all_day=False,
                    location={
                        'name': 'City Hall',
                        'address': '121 N LaSalle St Chicago, IL 60602'
                    },
                    source=response.url,
                    links=self._parse_links(column, start, response),
                )
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
    def parse_description(response):
        desc_xpath = '//p[contains(text(), "The Chicago Plan Commission")]/text()'
        description = response.xpath(desc_xpath).extract_first(default='').strip()
        return description

    @staticmethod
    def parse_meetings(response):
        meeting_xpath = """
            //td[preceding::p/strong[1]/text()[
                contains(., "Meeting Schedule")
                ]]"""
        return response.xpath(meeting_xpath)

    @staticmethod
    def _parse_start(meeting, year):
        m = re.search(r'(?P<month>\w+)\.?\s(?P<day>\d+).*', meeting.strip())
        if not m:
            return
        dt = dateutil.parser.parse(m.group('month') + ' ' + m.group('day') + ' ' + year)
        # time based on examining meeting minutes
        return datetime.combine(dt.date(), time(10))

    @staticmethod
    def _parse_links(item, start, response):
        month = start.strftime("%B")
        xp = './/a[contains(@title, "{0}")]'.format(month)
        documents = item.xpath(xp)
        if len(documents) >= 0:
            return [{
                'href': response.urljoin(document.xpath('@href').extract_first()),
                'title': document.xpath('text()').extract_first()
            } for document in documents]
        return []
