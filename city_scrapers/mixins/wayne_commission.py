# THIS IS JUST A MIXIN. IT MAY USE THINGS THAT ARE NOT ACTUALLY USABLE YET,
# BUT IT WILL BE INTEGRATED INTO A REGULAR AGENCY SPIDER.

# -*- coding: utf-8 -*-
import re
from datetime import datetime
from dateutil.parser import parse as dateparse
from urllib.parse import urljoin


class Wayne_commission:
    timezone = 'America/Detroit'
    allowed_domains = ['www.waynecounty.com']

    # Calendar shows only meetings in current year.
    yearStr = datetime.now().year

    @staticmethod
    def _parse_documents(item, base_url):
        url = item.xpath('td/a/@href').extract_first()
        url = urljoin(base_url, url) if url is not None else ''
        if url != '':
            note = item.xpath('td/a/text()').extract_first()
            note = note.lower() if note is not None else ''
            return [{
                'url': url,
                'note': note
            }]
        return []

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        # Dateparse can't always handle the inconsistent dates, so
        # let's normalize them using scrapy's regular expressions.
        month_str = item.xpath('.//td[2]/text()').re(r'[a-zA-Z]{3}')[0]
        day_str = item.xpath('.//td[2]/text()').re(r'\d+')[0]
        time_str = item.xpath('.//td[3]/text()').extract_first()
        date_str = dateparse('{0} {1} {2} {3}'.format(month_str, day_str, self.yearStr, time_str))

        return {'date': date_str.date(), 'time': date_str.time(), 'note': ''}

    def _parse_status(self, item, data):
        """
        Parse or generate status of meeting.
        Postponed meetings will be considered cancelled.
        """

        status_str = item.xpath('.//td[4]/a/text() | .//td[4]/text()').extract_first()
        # If the agenda column text contains "postponed," we consider it cancelled.
        if re.search(r'postpone', status_str, re.IGNORECASE):
            return 'cancelled'
        # If it's not cancelled, use the status logic from spider.py
        else:
            return self._generate_status(data, '')
