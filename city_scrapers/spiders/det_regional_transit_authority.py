from city_scrapers_core.constants import ADVISORY_COMMITTEE, BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class DetRegionalTransitAuthoritySpider(CityScrapersSpider):
    name = 'det_regional_transit_authority'
    agency = 'Regional Transit Authority of Southeast Michigan'
    timezone = 'America/Detroit'
    allowed_domains = ['www.rtamichigan.org']
    start_urls = ['http://www.rtamichigan.org/board-and-committee-meetings/']
    location = {
        'name': 'RTA Office',
        'address': '1001 Woodward Ave, Suite 1400, Detroit, MI 48226',
    }

    def parse(self, response):
        for item in self._parse_meetings(response):
            title = item.xpath('text()').extract_first('')
            table_rows_excluding_header = item.xpath('following::table[1]//tr[position() > 1]')
            for row in table_rows_excluding_header:
                start = self._parse_start(row)
                # Skip meetings that are still TBD re: date
                if start is None:
                    continue
                meeting = Meeting(
                    title=title,
                    description='',
                    classification=self._parse_classification(title),
                    start=start,
                    end=None,
                    time_notes='',
                    all_day=False,
                    location=self.location,
                    links=self._parse_links(row),
                    source=response.url,
                )
                alert = ' '.join(row.xpath('td[3]//text()').extract())
                meeting['status'] = self._get_status(meeting, text=alert)
                meeting['id'] = self._get_id(meeting)
                yield meeting

    @staticmethod
    def _parse_meetings(response):
        committee_xpath = """
        //h4[
            text() = "Board of Directors" or
            text() = "Citizens Advisory Committee" or
            text() = "Executive and Policy Committee" or
            text() = "Finance and Budget Committee" or
            text() = "Funding Allocation Committee" or
            text() = "Planning and Service Coordination Committee" or
            text() = "Providers Advisory Council"
        ]
        """
        return response.xpath(committee_xpath)

    @staticmethod
    def _parse_classification(item):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        classifications = {
            'Board of Directors': BOARD,
            'Citizens Advisory Committee': ADVISORY_COMMITTEE,
            'Executive and Policy Committee': COMMITTEE,
            'Finance and Budget Committee': COMMITTEE,
            'Funding Allocation Committee': COMMITTEE,
            'Planning and Service Coordination Committee': COMMITTEE,
            'Providers Advisory Council	Advisory': COMMITTEE
        }
        return classifications.get(item, NOT_CLASSIFIED)

    @staticmethod
    def _parse_start(row):
        """
        Parse start date and time.
        """
        date_str = row.xpath('td[1]/text()').extract_first('')
        time_str = row.xpath('td[2]/text()').extract_first('')
        try:
            return parse("{} {}".format(date_str, time_str))
        except ValueError:
            pass

    @staticmethod
    def _parse_links(item):
        """Parse or generate links."""
        anchors = item.xpath('.//a')
        return [{
            'href': anchor.xpath('@href').extract_first(''),
            'title': anchor.xpath('.//text()').extract_first('')
        } for anchor in anchors]
