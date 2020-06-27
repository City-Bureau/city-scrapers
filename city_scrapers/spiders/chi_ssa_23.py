import re
import unicodedata
from datetime import datetime, timedelta

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa23Spider(CityScrapersSpider):
    name = "chi_ssa_23"
    agency = "Chicago Special Service Area #23 Clark Street"
    timezone = "America/Chicago"
    start_urls = ["https://www.lincolnparkchamber.com/clark-street-ssa-administration/"]
    location = {
        "name": "Lincoln Park Chamber of Commerce",
        "address": "2468 N. Lincoln Chicago, IL 60614",
    }
    # Each meeting takes place on Wednesday 4 PM
    meeting_day = "Wednesday"
    time = "4:00 pm"

    def parse(self, response):

        address_text = response.xpath('//div[@class = "address"][1]/text()').extract()[
            1
        ]
        self._validate_location(address_text)

        h4s = response.xpath("//h4")

        # General meeting description is mentioned just after the H4 for current year
        general_desc = h4s.xpath("following-sibling::p[1]//em//text()").extract_first()

        # Dictionary containing all meeting dictionaries
        # The dates will be the keys
        meetings = dict()

        last_year = datetime.today().replace(year=datetime.today().year - 1)

        for entry_cnt, entry in enumerate(h4s, start=1):
            entry_str = entry.xpath("./text()").extract_first()
            test_year = entry_str[0:4]

            if "Schedule" in entry_str:

                for item in entry.xpath(
                    "following-sibling::ol[1]//li//text()"
                ).getall():
                    date, start, end = self._parse_date_start_end(item, test_year)

                    meetings[date] = {
                        "start": start,
                        "end": end,
                        # Scheduled appointments have no links
                        "links": [],
                    }

            elif "Agendas" in entry_str or "Minutes" in entry_str:

                # Only consider ps between two h4s
                for p in entry.xpath(
                    "following-sibling::p[count(preceding-sibling::h4)=" "$entry_cnt]",
                    entry_cnt=entry_cnt,
                ):

                    # The  non-breaking space signals the end of the meeting lists
                    if (
                        p.xpath("./text()")
                        and "\xa0" in p.xpath("./text()").extract_first()
                    ):
                        break

                    for item in p.xpath("./a"):

                        item_str = item.xpath("./text()").extract_first()
                        date, start, end = self._parse_date_start_end(
                            item_str, test_year
                        )

                        item_links = item.xpath("@href").extract()
                        links = self._parse_links(item_links, entry_str)

                        if date in meetings:

                            meetings[date]["links"].extend(links)

                        else:

                            meetings[date] = {
                                "start": start,
                                "end": end,
                                "links": links,
                            }

        # Create the meeting objects
        for key, item in meetings.items():

            if item["start"] < last_year and not self.settings.getbool(
                "CITY_SCRAPERS_ARCHIVE"
            ):
                continue

            meeting = Meeting(
                title="Commission",
                description=unicodedata.normalize("NFKD", general_desc),
                classification=COMMISSION,
                start=item["start"],
                end=item["end"],
                time_notes="Estimated 90 minutes duration",
                all_day=False,
                location=self.location,
                links=item["links"],
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_date_start_end(self, item, year):
        """
        Parse start date and time.
        """
        # Check for explicit start times in the string
        try:
            start_time = re.search(r"\((.*?)\)", item).group(1)

        except AttributeError:
            start_time = self.time

        # Split the month day string and make sure to drop the year before that
        dm_str = item.split(",")[0].split()

        # Adding a 0 as padding for single-digit days
        if len(dm_str[1]) < 2:
            dm_str[1] = "0" + dm_str[1]
        dt_str = dm_str[0] + " " + dm_str[1]

        start = datetime.strptime(
            "{} {} {} {}".format(
                self.meeting_day, re.sub(r"[,\.]", "", dt_str), start_time, year
            ),
            "%A %B %d %I:%M %p %Y",
        )
        date = start.date()
        end = start + timedelta(minutes=90)

        return date, start, end

    def _parse_links(self, items, entry_str):
        documents = []
        for url in items:
            if url:
                documents.append(self._build_link_dict(url, entry_str))

        return documents

    def _build_link_dict(self, url, entry_str):
        if "agenda" in entry_str.lower():
            return {"href": url, "title": "Agenda"}
        elif "minutes" in entry_str.lower():
            return {"href": url, "title": "Minutes"}
        else:
            return {"href": url, "title": "Link"}

    def _validate_location(self, text):
        """Parse or generate location."""
        if "2468" not in text:
            raise ValueError("Meeting location has changed")
