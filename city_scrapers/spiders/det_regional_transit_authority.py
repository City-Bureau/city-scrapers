# -*- coding: utf-8 -*-

from dateutil.parser import parse

from city_scrapers.spider import Spider


class DetRegionalTransitAuthoritySpider(Spider):
    name = 'det_regional_transit_authority'
    agency_id = 'Regional Transit Authority of Southeast Michigan'
    timezone = 'America/Detroit'
    allowed_domains = ['www.rtamichigan.org']
    start_urls = ['http://www.rtamichigan.org/board-and-committee-meetings/']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        location = {'neighborhood': '',
                    'name': 'RTA Office',
                    'address': '1001 Woodward Avenue, Suite 1400, Detroit, MI 48226'}
        for item in self._parse_meetings(response):
            name = item.xpath('text()').extract_first('')
            table_rows_excluding_header = item.xpath('following::table[1]//tr[position() > 1]')
            for row in table_rows_excluding_header:
                start = self._parse_start(row)
                # Skip meetings that are still TBD re: date
                if start['date'] is None:
                    continue
                data = {
                    '_type': 'event',
                    'name': name,
                    'event_description': '',
                    'classification': self._parse_classification(name),
                    'start': start,
                    'end': {'date': None, 'time': None, 'note': ''},
                    'all_day': False,
                    'location': location,
                    'documents': self._parse_documents(row),
                    'sources': [{'url': response.url, 'note': ''}]
                }
                alert = row.xpath('td[3]/text()').extract_first('')
                data['status'] = self._generate_status(data, text=alert)
                data['id'] = self._generate_id(data)
                yield data

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
            'Board of Directors': 'Board',
            'Citizens Advisory Committee': 'Advisory Committee',
            'Executive and Policy Committee': 'Committee',
            'Finance and Budget Committee': 'Committee',
            'Funding Allocation Committee': 'Committee',
            'Planning and Service Coordination Committee': 'Committee',
            'Providers Advisory Council	Advisory': 'Committee'
        }
        return classifications.get(item, '')

    @staticmethod
    def _parse_start(row):
        """
        Parse start date and time.
        """
        date = row.xpath('td[1]/text()').extract_first('')
        time = row.xpath('td[2]/text()').extract_first('')
        date_str = "{} {}".format(date, time)
        try:
            dt = parse(date_str)
            return {'date': dt.date(), 'time': dt.time(), 'note': ''}
        except ValueError:
            return {'date': None, 'time': None, 'note': date_str}

    @staticmethod
    def _parse_documents(item):
        """
        Parse or generate documents.
        """
        anchors = item.xpath('.//a')
        return [{'url': anchor.xpath('@href').extract_first(''),
                 'note': anchor.xpath('.//text()').extract_first('')}
                for anchor in anchors]
