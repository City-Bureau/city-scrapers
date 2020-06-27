import re
from datetime import datetime

from city_scrapers_core.constants import COMMISSION, PASSED, TENTATIVE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy.selector import Selector


class ChiMidwayNoiseSpider(CityScrapersSpider):
    name = "chi_midway_noise"
    agency = "Chicago Midway Noise Compatibility Commission"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.flychicago.com/community/MDWnoise/AdditionalResources/pages/default.aspx"  # noqa
    ]
    title = "Midway Noise Compatibility Commission Meeting"
    location = {
        "name": "The Mayfield",
        "address": "6072 S. Archer Ave., Chicago, IL 60638",
    }
    source = "https://www.flychicago.com/community/MDWnoise/AdditionalResources/pages/default.aspx"  # noqa

    def parse(self, response):
        """
        This page contains meetings in two different sections, which are formatted
        differently and contain some duplication. For this reason the meeting properties
        will be scraped from their separate sections, and only at the end converted into
        Meeting objects and yielded as a list with the 'yield from ...' behavior.
        """

        candidates = (
            list()
        )  # Elements will be dicts having Meeting property names as keys

        # Process the meetings presented in the "Commission Meetings" table:
        selector_str = "//h3/following-sibling::table/tbody/tr"
        for item in response.xpath(selector_str):
            if "<br>" in item.extract():
                # Requires special treatment. See _parse_malformed_row() for details.
                candidates.extend(self._parse_malformed_row(item, response))
                continue
            candidates.append(
                {
                    "title": self._parse_title(item),
                    "start": self._parse_start(item),
                    "links": self._parse_links(item, response),
                }
            )

        # Process the meetings presented in "Commission Meeting Schedule for ...":
        selector_str = "(//h3/following-sibling::ul)[1]/li/text()"
        for item in response.xpath(selector_str):
            start = self._parse_start(item)
            if start is None:  # Skip this item if start time could not be determined
                continue
            # Skip if start date in the past, because captured above
            if start < datetime.now():
                continue
            candidates.append({"title": "Commission", "start": start, "links": []})

        last_year = datetime.today().replace(year=datetime.today().year - 1)
        meeting_list = []
        for elem in candidates:
            if not elem["start"] or (
                elem["start"] < last_year
                and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE")
            ):
                continue
            meeting = Meeting(
                title=elem["title"],
                description="",
                classification=COMMISSION,
                start=elem["start"],
                end=None,
                all_day=False,
                time_notes="No start times given; past records indicate 6:30PM.",
                location=self.location,
                links=elem["links"],
                source=self.source,
                status=self._parse_status(elem["start"]),
            )
            meeting["id"] = self._get_id(meeting)
            meeting_list.append(meeting)

        yield from meeting_list

    def _parse_title(self, item):
        if type(item) == Selector:
            item = item.get()
        text = self._clean_bad_chars(item)
        desc = ""
        if "Regular" in text:
            desc = "Commission"
        elif "Special" in text:
            desc = "Special Meeting"
        elif "Committee" in text:
            desc = "Committee"
            if "Executive" in text:
                desc = "Executive {}".format(desc)
            elif "Residential" in text:
                desc = "Residential {}".format(desc)
        return desc

    def _parse_start(self, item):
        """Parse the meeting start time."""
        # No (clock) times are given on the site, but records of past meetings show a
        # consistent 6:30PM start time.
        date = self._parse_date(item)
        if date is None:
            return None
        return datetime(date["year"], date["month"], date["day"], 18, 30)

    def _parse_date(self, item):
        """Parse the meeting date."""
        if type(item) == Selector:
            # Scheduled meetings have only text; past meetings have <td> tags.
            if "<td>" in item.get():
                item = item.xpath(".//td/text()").get()
            else:
                item = item.get()
        item = self._clean_bad_chars(item)
        regex = re.compile(r"(?P<month>[a-zA-Z]+) (?P<day>[0-9]+), (?P<year>[0-9]{4})")
        m = regex.search(item)

        try:
            return {
                "month": datetime.strptime(m.group("month"), "%B").month,
                "day": int(m.group("day")),
                "year": int(m.group("year")),
            }
        except AttributeError:  # Regex failed to match.
            return None

    def _parse_links(self, item, response):
        """Parse or generate links."""
        documents = []
        if type(item) == Selector:
            relative_urls = item.xpath(".//a/@href").extract()
            for relative_url in relative_urls:
                documents.append(self._build_link_dict(response.urljoin(relative_url)))
        else:
            elems = item.split(",")
            for elem in elems:
                regex = re.compile(r'<a href="(?P<url>.*?)"')
                m = regex.search(elem)
                try:
                    relative_url = m.group("url")
                    documents.append(
                        self._build_link_dict(response.urljoin(relative_url))
                    )
                except AttributeError:
                    continue  # Not a problem, some of these do not contain links.
        return documents

    def _parse_status(self, start):
        """Parse scheduling status."""
        if start > datetime.now():
            return TENTATIVE
        else:
            return PASSED

    def _parse_malformed_row(self, item, response):
        """
        Parse a special case of meeting information.

        This row diverges from the previous pattern in that it uses <br> tags within
        <td> cells instead of new <tr> tags for table rows.

        The first (left-most) <td> contains the <br>-separated list of meeting dates and
        types. The second (right-most) <td> contains the <br>-separated list of agenda
        and minutes links.
        """

        tds = item.xpath(".//td")
        dates_and_types = (
            tds[0].extract().replace("<td>", "").replace("</td>", "").split("<br>")
        )
        links = tds[1].extract().replace("<td>", "").replace("</td>", "").split("<br>")

        candidates = list()
        for pair in zip(dates_and_types, links):
            candidates.append(
                {
                    "title": self._parse_title(pair[0]),
                    "start": self._parse_start(pair[0]),
                    "links": self._parse_links(pair[1], response),
                }
            )

        return candidates

    def _clean_bad_chars(self, text):
        """ Remove unwanted unicode characters (only one found so far). """
        return text.replace("\u200b", "")

    def _build_link_dict(self, url):
        if "agenda" in url.lower():
            return {"href": url, "title": "Agenda"}
        elif "minutes" in url.lower():
            return {"href": url, "title": "Minutes"}
        else:
            return {"href": url, "title": "Link"}
