import re
from datetime import datetime, time

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSchoolsSpider(CityScrapersSpider):
    name = 'chi_schools'
    agency = 'Chicago Public Schools'
    timezone = 'America/Chicago'
    start_urls = [
        'http://www.cpsboe.org/meetings/planning-calendar',
        'https://www.cpsboe.org/meetings/past-meetings',
    ]

    def parse(self, response):
        description = self._parse_description(response)
        for idx, item in enumerate(response.css('#content-primary tr')):
            if idx == 0 and 'calendar' in response.url:
                continue
            if 'calendar' in response.url:
                start = self._parse_start_time(item)
            else:
                start = self._parse_past_start(item)
            if start is not None:
                meeting = Meeting(
                    title=self._parse_title(item, response),
                    description=description,
                    classification=BOARD,
                    start=start,
                    end=None,
                    time_notes='',
                    all_day=False,
                    location=self._parse_location(item),
                    links=self._parse_links(item, start, response),
                    source=self._parse_source(item, response),
                )
                meeting['id'] = self._get_id(meeting)
                meeting['status'] = self._get_status(meeting, text=description)
                yield meeting

    def _parse_title(self, item, response):
        title = 'Board of Education'
        alt_title = item.css('.mute::text').extract_first()
        if 'past' in response.url and alt_title is not None:
            title = re.sub(r'[\(\)]', '', alt_title)
        return title

    def _parse_description(self, response):
        desc_xpath = '//table/following-sibling::ul//text()|//table/following-sibling::p//text()'
        desc_text = response.xpath(desc_xpath).extract()
        if len(desc_text) == 0:
            return ''
        return ' '.join(desc_text)

    def _remove_line_breaks(self, collection):
        return [x.strip() for x in collection if x.strip() != '']

    def _parse_start_time(self, item):
        raw_strings = item.css('::text').extract()
        date_string_list = self._remove_line_breaks(raw_strings)
        date_string = ''
        if len(date_string_list) > 0:
            date_string = date_string_list[0]
        date_string = date_string.replace(' at', '')
        date_string = date_string.replace(',', "").replace(':', " ")
        try:
            return datetime.strptime(date_string, '%B %d %Y %I %M %p')
        except Exception:
            pass

    def _parse_past_start(self, item):
        date_str = item.css('th a::text').extract_first()
        date_obj = datetime.strptime(date_str.strip(), '%B %d, %Y').date()
        return datetime.combine(date_obj, time(8, 30))

    def _parse_location(self, item):
        raw_text_list = item.css('::text').extract()
        text_list = self._remove_line_breaks(raw_text_list)[1:]
        text_list = [x for x in text_list if '(' not in x and ')' not in x]
        address = " ".join(text_list)
        if 'actions' in address.lower():
            return {
                'name': 'CPS Loop Office',
                'address': '42 W Madison St, Board Room, Chicago, IL 60602',
            }
        loop_office = 'CPS Loop Office'
        if loop_office in address:
            return {
                'address': address.replace(loop_office, '').strip(),
                'name': loop_office,
            }
        return {
            'address': address,
            'name': '',
        }

    def _parse_links(self, item, start, response):
        documents = []
        for doc_link in item.css('td a'):
            doc_url = response.urljoin(doc_link.attrib['href'])
            doc_note = doc_link.css('::text').extract_first()
            if doc_note.lower() == 'proceedings':
                mo_str = start.strftime('%b').lower()
                doc_url = response.urljoin(
                    '/content/documents/{}{dt.day}_{dt.year}proceedings.pdf'.format(
                        mo_str, dt=start
                    )
                )
            documents.append({
                'href': doc_url,
                'title': doc_note,
            })
        return documents

    def _parse_source(self, item, response):
        """Parse source."""
        if 'past' in response.url:
            detail_url = item.css('th a')[0].attrib['href']
            return response.urljoin(detail_url)
        return response.url
