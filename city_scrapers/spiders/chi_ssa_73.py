import re
from datetime import datetime, time

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa73Spider(CityScrapersSpider):
    name = "chi_ssa_73"
    agency = "Chicago Special Service Area #73 Chinatown"
    timezone = "America/Chicago"
    start_urls = ["https://chinatownssa73.org/meeting-schedule/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        links_list = self._get_links(response)
        location = self._parse_location(response)
        ids_list = []
        start_time = self._parse_time(response)
        for item in response.css("article p"):
            start = self._parse_start(item, start_time)
            if not start:
                continue
            meeting = Meeting(
                title="SSA #73 Chinatown Board",
                description="",
                classification=BOARD,
                start=start,
                end=None,
                all_day=False,
                time_notes="",
                location=location,
                links=self._parse_links(item, start, links_list),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            if meeting["id"] in ids_list:
                continue
            else:
                ids_list.append(meeting["id"])

            yield meeting

    def _parse_start(self, item, start_time):
        """
        Parse start date and time.
        """
        date_str = item.css("*::text").extract_first()
        if not date_str:
            return
        date_match = re.search(r"\w{3,9} \d{1,2}, \d{4}", date_str)
        if date_match:
            parsed_date = datetime.strptime(date_match.group(), "%B %d, %Y")
            return datetime.combine(parsed_date.date(), start_time.time())

    def _parse_time(self, response):
        first_line = response.css("article p").extract_first()
        time_match = re.search(r"\d{1,2}:\d{2} [ap]\.m", first_line)
        if time_match:
            temp_str = time_match.group()
            temp_str = temp_str.replace(".", "")
            temp_str = temp_str.upper()
            return datetime.strptime(temp_str, "%I:%M %p")
        else:
            return time(18, 30)

    def _parse_location(self, response):
        """
        Parse or generate location.
        """
        if "1700 S. Wentworth" in response.text:
            return {
                "address": "1700 S. Wentworth Avenue, Chicago, Illinois",
                "name": "Leonard M. Louie Fieldhouse",
            }
        elif "Zoom" in response.text:
            return {
                "address": "",
                "name": "Zoom",
            }
        else:
            raise ValueError("Meeting address has changed")

    def _get_links(self, response):
        links_list = []
        for item in response.css("a"):
            new_dict = {}
            add_link = False
            if "Agenda" in item.extract():
                new_dict["title"] = "Agenda"
                add_link = True
            elif "Minutes" in item.extract():
                new_dict["title"] = "Minutes"
                add_link = True
            if add_link:
                new_dict["href"] = item.attrib["href"]
                raw_ref = item.css("*::text").extract_first()
                new_dict["date"] = raw_ref.split()[1]
                links_list.append(new_dict)
        return links_list

    def _parse_links(self, item, start, links_list):
        """Parse or generate links."""
        result_list = []
        target_str_1 = start.strftime("%m-%d-%Y").replace(" 0", " ")
        target_str_2 = start.strftime("%m-%d-%y").replace(" 0", " ")
        for item in links_list:
            if item["date"] in target_str_1 or item["date"] in target_str_2:
                new_dict = {}
                new_dict["href"] = item["href"]
                new_dict["title"] = item["title"]
                result_list.append(new_dict)
        return result_list
