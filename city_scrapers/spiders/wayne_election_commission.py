import re

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class WayneElectionCommissionSpider(CityScrapersSpider):
    name = 'wayne_election_commission'
    agency = 'Wayne County Election Commission'
    timezone = 'America/Detroit'
    start_urls = ['https://www.waynecounty.com/elected/clerk/election-commission.aspx']
    location = {
        'name': 'Coleman A. Young Municipal Center, Conference Room 700A',
        'address': '2 Woodward Ave, Detroit, MI 48226'
    }

    def parse(self, response):
        non_empty_rows_xpath = '//tbody/tr[child::td]'
        for item in response.xpath(non_empty_rows_xpath):
            start = self._parse_start(item)
            if start is None:
                continue
            meeting = Meeting(
                title='Election Commission',
                description='',
                classification=COMMISSION,
                start=start,
                end=None,
                time_notes='',
                all_day=False,
                location=self.location,
                links=self._parse_links(item, response),
                source=response.url,
            )
            meeting['status'] = self._get_status(meeting)
            meeting['id'] = self._get_id(meeting)
            yield meeting

    @staticmethod
    def _parse_start(item):
        """Parse start datetime."""
        year_xpath = item.xpath('ancestor::table/thead//strong/text()').extract_first()
        year_regex = re.compile(r'\d{4}')
        year_str = year_regex.findall(year_xpath)[0]
        month_day_str = item.xpath('td[1]//text()').extract_first()
        try:
            return parse(month_day_str + ", " + year_str)
        except Exception:
            return

    def _parse_links(self, item, response):
        """
        Parse or generate documents.
        """
        tds = item.xpath('td[position() >1]')
        return [self._build_document(td, response) for td in tds if self._has_url(td)]

    @staticmethod
    def _has_url(td):
        return td.xpath('.//@href').extract_first()

    @staticmethod
    def _build_document(td, response):
        document_url = response.urljoin(td.xpath('.//@href').extract_first())
        text = td.xpath('.//text()').extract_first()
        return {'href': document_url, 'title': text}
