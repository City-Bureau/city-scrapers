import re
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiPoliceRetirementSpider(CityScrapersSpider):
    name = "chi_police_retirement"
    agency = "Policemen's Annuity and Benefit Fund of Chicago"
    timezone = "America/Chicago"
    allowed_domains = ["www.chipabf.org"]
    start_urls = ["http://www.chipabf.org/ChicagoPolicePension/MonthlyMeetings.html"]
    TAG_RE = re.compile(r'<[^>]+>')

    def parse(self, response):
        year = self._parse_year(response)
        date_table = response.xpath('//*[@id="content0"]/div[3]/table')
        date_items = date_table.extract()[0].split('<tr>')

        skip_first_item = True
        for item in date_items:
            if skip_first_item:
                skip_first_item = False
                continue

            meeting = Meeting(
                title=self._parse_title(response),
                description=self._parse_description(response),
                classification=self._parse_classification(response),
                start=self._parse_start(item, year),
                time_notes=self._parse_time_notes(),
                end=self._parse_end(),
                all_day=False,
                location=self._parse_location(response),
                source=self._parse_source(response),
                links=self._parse_links(item)
            )

            # replace before this
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return "Board Meetings of The Policemen\'s Annuity & Benefit Fund"

    def _parse_description(self, response):
        """Parse or generate meeting description."""
        raw_description = ''.join(response.xpath('//*[@id="content0"]/p/text()').extract())
        clean_description = self._clean_escape_chars(raw_description)
        print(repr(' '.join(clean_description.split())))
        return ' '.join(clean_description.split())

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return BOARD

    def _parse_start(self, item, year):
        start = self._get_date_string(item, year)
        return datetime.strptime(start, '%B %d %Y %I%p')

    def _parse_time_notes(self):
        return None

    def _parse_end(self):
        return None

    # see here for address: http://www.chipabf.org/ChicagoPolicePension/aboutus.html
    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "221 North LaSalle Street, Suite 1626,"
                       " Chicago, Illinois 60601-1203",
            "name": "Policemen's Annuity and Benefit Fund",
        }

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url

    def _parse_links(self, item):
        links = []
        raw_links = item.split('a href')
        if len(raw_links) > 1:
            raw_agenda = raw_links[1]
            file_path = re.search(r'\"(.+?)\"', raw_agenda).group(1)
            title = re.search(r'\>(.+?)\<', self._clean_escape_chars(raw_agenda)).group(1).strip()
            agenda = {
                "href": 'https://' + self.allowed_domains[0] + '/ChicagoPolicePension/' + file_path,
                "title": title
            }
            links.append(agenda)

        if len(raw_links) > 2:
            raw_minutes = raw_links[2]
            file_path = re.search(r'\"(.+?)\"', raw_minutes).group(1)
            title = re.search(r'\>(.+?)\<', raw_minutes).group(1).strip()
            minutes = {
                "href": self.allowed_domains[0] + '/ChicagoPolicePension/' + file_path,
                "title": title
            }
            links.append(minutes)
        return links

    def _parse_year(self, item):
        return item.xpath('//*[@id="content0"]/div[3]/h2[1]/text()').extract()[0][:4]

    def _clean_html_tags(self, item):
        return self.TAG_RE.sub('', item).strip()

    def _clean_escape_chars(self, s, space=False):
        d_tab = s.replace('\t', '')
        d_newl = d_tab.replace('\n', '')
        if not space:
            clean_s = d_newl.replace('\r', '')
        else:
            clean_s = d_newl.replace('\r', ' ')
        return clean_s

    def _get_date_string(self, item, year):
        no_tags = self._clean_html_tags(item)
        date_pieces = no_tags.split()
        date_pieces[3] = ''.join([num for num in date_pieces[3] if num.isdigit()])
        date = ' '.join(date_pieces[2:4]) + ' ' + year + ' ' + date_pieces[4]
        return date
