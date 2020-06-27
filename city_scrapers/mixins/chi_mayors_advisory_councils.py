import datetime
import re

from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from lxml import etree


class ChiMayorsAdvisoryCouncilsMixin:
    timezone = "America/Chicago"
    BASE_URL = "http://chicagocompletestreets.org/getinvolved/mayors-advisory-councils/"
    title = ""

    def _parse_archive_documents(self, response):
        """
        Documents live in a series of <p> elements, structured like:

            Year
            Month Day, Year Agenda – Meeting Minutes – Presentations

        There is a line for each scheduled meeting. Agenda, Meeting Minutes,
        and Presentations are links, where there is a document available.
        """
        for p in response.xpath("//p"):
            if self._contains_year(p):
                blob = p.extract().splitlines()
                yield from self._parse_document_blob(blob)

    def _contains_year(self, element):
        return element.xpath("text()") and re.match(
            r"\d{4}", element.xpath("text()")[0].extract()
        )

    def _tree_from_fragment(self, fragment):
        """
        Coerce HTML fragments from into parse-able blobs.
        """
        return etree.HTML(fragment).xpath("//p")[0]

    def _parse_document_blob(self, blob):
        for line in blob[1:]:  # Omit header
            element = self._tree_from_fragment(line)

            date = " ".join(element.text.split(" ")[:3])

            documents = []

            for doc in element.iterchildren("a"):
                documents.append(
                    {"href": doc.attrib["href"], "title": doc.text.strip()}
                )

            yield date, documents

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for date, documents in self._parse_archive_documents(response):
            meeting = Meeting(
                title=self.title,
                description="",
                classification=ADVISORY_COMMITTEE,
                start=self._parse_start(date),
                end=None,
                time_notes="Start at 3 p.m. unless otherwise noted",
                all_day=False,
                location=self.location,
                links=documents,
                source=self.BASE_URL,
            )

            meeting["status"] = self._get_status(meeting, text="")
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_classification(self):
        """
        Parse or generate classification (e.g. public health, education, etc).
        """
        return ADVISORY_COMMITTEE

    def _parse_start(self, item):
        """
        Parse start date and time like "Wednesday, March 7, 2017."
        """
        date = datetime.datetime.strptime(item.strip(), "%B %d, %Y").date()
        mtg_time = datetime.time(15, 0)
        return datetime.datetime.combine(date, mtg_time)
