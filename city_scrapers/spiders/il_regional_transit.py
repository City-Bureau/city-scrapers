import re
from datetime import datetime, time

from city_scrapers_core.constants import ADVISORY_COMMITTEE, BOARD, COMMITTEE, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlRegionalTransitSpider(CityScrapersSpider):
    name = 'il_regional_transit'
    agency = 'Regional Transportation Authority'
    timezone = 'America/Chicago'
    start_urls = [
        'http://rtachicago.granicus.com/ViewPublisher.php?view_id=5',
        'http://rtachicago.granicus.com/ViewPublisher.php?view_id=4',
    ]
    custom_settings = {'ROBOTSTXT_OBEY': False}
    location = {
        'name': 'RTA Administrative Offices',
        'address': '175 W. Jackson Blvd, Suite 1650, Chicago, IL 60604',
    }

    def parse(self, response):
        for item in response.css('.row:not(#search):not(.keywords)'):
            start = self._parse_start(item)
            if start is None:
                continue
            title = self._parse_title(item)
            meeting = Meeting(
                title=title,
                description='',
                classification=self._parse_classification(title),
                start=start,
                end=None,
                time_notes='Initial meetings begin at 8:30am, with other daily meetings following',
                all_day=False,
                location=self.location,
                links=self._parse_links(item),
                source=response.url,
            )
            meeting['id'] = self._get_id(meeting)
            meeting['status'] = self._get_status(meeting)
            yield meeting

    @staticmethod
    def _parse_classification(name):
        name = name.upper()
        if 'CITIZENS ADVISORY' in name:
            return ADVISORY_COMMITTEE
        if 'COMMITTEE' in name:
            return COMMITTEE
        if 'BOARD' in name:
            return BOARD
        return NOT_CLASSIFIED

    @staticmethod
    def _parse_title(item):
        name_text = item.css('.committee::text').extract_first()
        name_text = name_text.split(' on ')[0].split(' (')[0]
        name_text = re.sub(r'\d{1,2}:\d{2}\s+[APM]{2}', '', name_text)
        return name_text.strip()

    @staticmethod
    def _parse_start(item):
        """
        Retrieve the event date, always using 8:30am as the time.
        """
        date_str = ' '.join(item.css('div:first-child::text').extract()).strip()
        date_obj = datetime.strptime(date_str, '%b %d, %Y').date()
        return datetime.combine(date_obj, time(8, 30))

    @staticmethod
    def _parse_links(item):
        documents = []
        for doc_link in item.css('a'):
            if 'onclick' in doc_link.attrib:
                doc_url = re.search(r'(?<=window\.open\(\').+(?=\',)',
                                    doc_link.attrib['onclick']).group()
                if doc_url.startswith('//'):
                    doc_url = 'http:' + doc_url
            else:
                doc_url = doc_link.attrib['href']
            doc_note = doc_link.css('img::attr(alt)').extract_first()
            # Default to link title if alt text for doc icon isn't available
            if doc_note is None:
                if 'title' in doc_link.attrib:
                    doc_note = doc_link.attrib['title']
                else:
                    continue
            if 'listen' in doc_note.lower():
                doc_note = 'Audio'
            elif 'agenda' in doc_note.lower():
                doc_note = 'Agenda'
            elif 'minutes' in doc_note.lower():
                doc_note = 'Minutes'
            elif 'video' in doc_note.lower():
                doc_note = 'Video'
            documents.append({
                'href': doc_url,
                'title': doc_note,
            })
        return documents
