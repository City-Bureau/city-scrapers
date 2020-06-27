import re
from datetime import datetime

from city_scrapers_core.constants import BOARD, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiPoliceRetirementSpider(CityScrapersSpider):
    name = "chi_police_retirement"
    agency = "Policemen's Annuity and Benefit Fund of Chicago"
    timezone = "America/Chicago"
    start_urls = ["http://www.chipabf.org/ChicagoPolicePension/MonthlyMeetings.html"]
    TAG_RE = re.compile(r"<[^>]+>")

    def parse(self, response):
        year = self._parse_year(response)
        board_items = (
            response.xpath('//*[@id="content0"]/div[3]/table')
            .extract()[0]
            .split("<tr>")
        )
        invest_items = (
            response.xpath('//*[@id="content0"]/div[2]/table')
            .extract()[0]
            .split("<tr>")
        )
        date_items = board_items + invest_items

        for date_item in date_items:
            if "table border" in date_item or "NONE" in date_item:
                continue
            start = self._parse_start(date_item, year)
            if not start:
                continue

            meeting = Meeting(
                title=self._parse_title(date_item),
                description="",
                classification=self._parse_classification(date_item),
                start=start,
                end=None,
                time_notes="",
                all_day=False,
                location=self._parse_location(),
                source=self._parse_source(response),
                links=self._parse_links(date_item, response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, date_item):
        """Parse or generate meeting title."""
        if "Board" in date_item:
            return "Retirement Board"
        else:
            return "Investment Committee"

    def _parse_classification(self, date_item):
        """Parse or generate classification from allowed options."""
        if "Board" in date_item:
            return BOARD
        else:
            return COMMITTEE

    def _parse_start(self, date_item, year):
        try:
            start = self._get_date_string(date_item, year)
            return datetime.strptime(start, "%B %d %Y %I%p")
        except (IndexError, ValueError):
            return

    # see here for address: http://www.chipabf.org/ChicagoPolicePension/aboutus.html
    def _parse_location(self):
        """Parse or generate location."""
        return {
            "address": "221 North LaSalle Street, Suite 1626,"
            " Chicago, Illinois 60601-1203",
            "name": "Policemen's Annuity and Benefit Fund",
        }

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url

    def _parse_links(self, date_item, response):
        links = []
        raw_links = date_item.split("a href")
        if len(raw_links) > 1:
            raw_agenda = raw_links[1]
            file_path = re.search(r"\"(.+?)\"", raw_agenda).group(1)
            title = (
                re.search(r"\>(.+?)\<", self._clean_escape_chars(raw_agenda))
                .group(1)
                .strip()
            )
            agenda = {"href": response.urljoin(file_path), "title": title}
            links.append(agenda)

        if len(raw_links) > 2:
            raw_minutes = raw_links[2]
            file_path = re.search(r"\"(.+?)\"", raw_minutes).group(1)
            title = "Minutes"
            title_match = re.search(r"\>(.+?)\<", raw_minutes)
            if title_match:
                title = title_match.group(1).strip()
            minutes = {"href": response.urljoin(file_path), "title": title}
            links.append(minutes)
        return links

    def _parse_year(self, response):
        return response.xpath('//*[@id="content0"]/div[3]/h2[1]/text()').extract()[0][
            :4
        ]

    def _clean_html_tags(self, date_item):
        date_item = date_item.replace("<br>", " ")
        return self.TAG_RE.sub("", date_item).strip()

    def _clean_escape_chars(self, s, space=False):
        d_tab = s.replace("\t", "")
        d_newl = d_tab.replace("\n", "")
        if not space:
            clean_s = d_newl.replace("\r", "")
        else:
            clean_s = d_newl.replace("\r", " ")
        return clean_s

    def _get_date_string(self, date_item, year):
        no_tags = self._clean_html_tags(date_item)
        date_pieces = no_tags.split()[-5:]
        date_pieces[1] = "".join([num for num in date_pieces[1] if num.isdigit()])
        date = " ".join(date_pieces[0:2]) + " " + year + " " + date_pieces[2]
        return date
