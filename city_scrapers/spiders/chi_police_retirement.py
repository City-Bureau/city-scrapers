from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider

import re
from datetime import datetime
from dateutil.parser import parse

def clean_escape_chars(s, space=False):
    d_tab = s.replace('\t', '')
    d_newl = d_tab.replace('\n', '')
    if not space:
        clean_s = d_newl.replace('\r', '')
    else:
        clean_s = d_newl.replace('\r', ' ')
    return clean_s

class ChiPoliceRetirementSpider(CityScrapersSpider):
    name = "chi_police_retirement"
    agency = "Policemen's Annuity and Benefit Fund of Chicago"
    timezone = "America/Chicago"
    allowed_domains = ["www.chipabf.org"]
    start_urls = ["http://www.chipabf.org/ChicagoPolicePension/MonthlyMeetings.html"]
    TAG_RE = re.compile(r'<[^>]+>')
    NOTES_RE = re.compile(r'^.*\-(.\D*).*$')

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        data = {
            '_type':'event',
            'name':'Board Meetings of The Policemen\'s Annuity & Benefit Fund',
            'event_description': self._parse_description(response),
            'classification': 'BOARD',
            'end': {
                'date': None,
                'time': None,
                'note': ''
            },
            'all_day': False,
            #http://www.chipabf.org/ChicagoPolicePension/aboutus.html
            'event_location':'221 North LaSalle Street, Suite 1626, Chicago, Illinois 60601-1203',
            'sources': [{
                'url': response.url,
                'note': ''
            }]
        }
        year = self._parse_year(response)

        date_table = response.xpath('//*[@id="content0"]/div[3]/table')
        date_items = date_table.extract()[0].split('<tr>')
        for item in date_items:
            print(item)
            start_date, start_time, notes = self._parse_start(item, year)
            new_item = {
                'start': {
                    'date': start_date,
                    'time': start_time,
                    'note': notes,
                },
                'documents': self._parse_documents(item),
            }
            new_item.update(data)
            new_item['id'] = self._generate_id(new_item)
            new_item['status'] = self._generate_status(new_item)
            yield new_item
        # for item in response.css(".meetings"):
        #     meeting = Meeting(
        #         title=self._parse_title(item),
        #         description=self._parse_description(item),
        #         classification=self._parse_classification(item),
        #         start=self._parse_start(item),
        #         end=self._parse_end(item),
        #         all_day=self._parse_all_day(item),
        #         time_notes=self._parse_time_notes(item),
        #         location=self._parse_location(item),
        #         links=self._parse_links(item),
        #         source=self._parse_source(response),
        #     )

        #     meeting["status"] = self._get_status(meeting)
        #     meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        raw_description = ''.join(item.xpath('//*[@id="content0"]/p/text()').extract())
        clean_description = clean_escape_chars(raw_description)
        return ' '.join(clean_description.split())

    def _parse_year(self, item):
        return item.xpath('//*[@id="content0"]/div[3]/h2[1]/text()').extract()[0][:4]

    def _parse_start(self, item, year):
        """Parse start datetime as a naive datetime object.

            return start date, start time, and notes
        """

        # strips table tags and escape chars
        date_string = clean_escape_chars(self.TAG_RE.sub('', item).strip(), True)

        # dash in the month indicates a note
        if '-' in date_string:
            note = self._parse_time_notes(date_string)
        else:
            note = ''
        print(date_string)
        dt = parse(date_string)
        start_time = dt.strftime('%R')
        start_date = dt.strftime('%B %d')

        return start_date, start_time, note

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        note = self.NOTES_RE.search(item)
        return note.group(1)

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]


