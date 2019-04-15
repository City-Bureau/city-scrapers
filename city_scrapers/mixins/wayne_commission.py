from datetime import datetime

from city_scrapers_core.constants import CANCELLED, COMMITTEE
from city_scrapers_core.items import Meeting
from dateutil.parser import parse as dateparse


class WayneCommissionMixin:
    timezone = 'America/Detroit'
    allowed_domains = ['www.waynecounty.com']
    classification = COMMITTEE
    location = {
        'name': '7th floor meeting room, Guardian Building',
        'address': '500 Griswold St, Detroit, MI 48226',
    }
    description = ''

    def parse(self, response):
        for item in self._parse_entries(response):
            meeting = Meeting(
                title=self.meeting_name,
                description=self.description,
                classification=self.classification,
                start=self._parse_start(item),
                end=None,
                time_notes='',
                all_day=False,
                location=self.location,
                links=self._parse_links(item, response),
                source=response.url,
            )
            meeting['id'] = self._get_id(meeting)
            status_str = ' '.join(item.xpath('.//td//text()').extract())
            meeting['status'] = self._get_status(meeting, text=status_str)
            yield meeting

    def _parse_entries(self, response):
        return response.xpath('//tbody/tr[child::td/text()]')

    @staticmethod
    def _parse_links(item, response):
        documents = []
        for doc_link in item.xpath('td/a'):
            url = doc_link.xpath('@href').extract_first()
            if url:
                note = doc_link.xpath('text()').extract_first()
                note = note if note is not None else ''
                documents.append({'href': response.urljoin(url), 'title': note})
        return documents

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        # Calendar shows only meetings in current year.
        year_str = datetime.now().year
        # Dateparse can't always handle the inconsistent dates, so
        # let's normalize them using scrapy's regular expressions.
        month_str = item.xpath('.//td[2]/text()').re(r'[a-zA-Z]{3}')[0]
        day_str = item.xpath('.//td[2]/text()').re(r'\d+')[0]
        time_str = item.xpath('.//td[3]/text()').extract_first()
        return dateparse('{0} {1} {2} {3}'.format(month_str, day_str, year_str, time_str))

    def _parse_status(self, item, meeting):
        """
        Parse or generate status of meeting.
        Postponed meetings will be considered cancelled.
        """
        status_str = item.xpath('.//td[4]//text()').extract_first()
        # If the agenda column text contains "postpone" or "cancel" we consider it cancelled.
        if ('cancel' in status_str.lower()) or ('postpone' in status_str.lower()):
            return CANCELLED
        # If it's not one of the above statuses, use the status logic from spider.py
        else:
            return self._get_status(meeting)
