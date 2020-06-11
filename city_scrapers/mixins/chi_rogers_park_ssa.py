import re
from collections import defaultdict
from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from dateutil.relativedelta import relativedelta


class ChiRogersParkSsaMixin:
    timezone = "America/Chicago"

    def parse(self, response):
        self.link_date_map = self._parse_links(response)
        for i in range(-3, 4):
            month_str = (datetime.now() + relativedelta(months=i)).strftime("%Y-%m")
            yield response.follow(
                "https://business.rpba.org/events/calendar/{}-01/".format(month_str),
                callback=self._parse_calendar,
            )

    def _parse_links(self, response):
        """Return a dictionary mapping start datetimes to documents"""
        link_dict = defaultdict(list)
        for section in response.css(".et_pb_tab_1 p, .et_pb_tab_2 p"):
            label_str = section.css("*::text").extract_first()
            if not label_str or (
                "Minutes" not in label_str and "Agenda" not in label_str
            ):
                continue
            year_str = label_str[:4]
            link_title = "Agenda" if "Agenda" in label_str else "Minutes"
            for link in section.css("a"):
                link_text = link.css("::text").extract_first().strip()
                if not re.match(r"^[a-zA-Z]{3,10} \d{1,2}$", link_text):
                    continue
                date_str = re.search(r"[a-zA-Z]{3,10} \d{1,2}", link_text).group()
                start = datetime.strptime(
                    "{} {}".format(date_str, year_str), "%B %d %Y"
                ).date()
                link_dict[start].append(
                    {"href": link.attrib["href"], "title": link_title}
                )
        return link_dict

    def _parse_calendar(self, response):
        ssa_num = re.search(r"#\d{1,2}", self.agency).group()
        for item in response.css(".mn-cal-event a"):
            item_text = " ".join(item.css("*::text").extract())
            if ssa_num in item_text:
                yield response.follow(item.attrib["href"], callback=self._parse_detail)

    def _parse_detail(self, response):
        start = self._parse_start(response)
        meeting = Meeting(
            title=self._parse_title(response),
            description="",
            classification=COMMISSION,
            start=start,
            end=self._parse_end(response),
            all_day=False,
            time_notes="",
            location=self._parse_location(response),
            links=self.link_date_map[start.date()],
            source=response.url,
        )

        meeting["status"] = self._get_status(meeting, text="TODO")
        meeting["id"] = self._get_id(meeting)
        yield meeting

    def _parse_title(self, response):
        title_str = " ".join(response.css("#mn-pagetitle *::text").extract())
        if "Emergency" in title_str:
            return "Emergency Meeting"
        if "special" in title_str.lower():
            return "Special Meeting"
        return "Commission"

    def _parse_start(self, response):
        date_str = response.css("[itemprop='startDate']::attr(content)").extract_first()
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M")

    def _parse_end(self, response):
        date_str = response.css("[itemprop='endDate']::attr(content)").extract_first()
        if date_str:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M")

    def _parse_location(self, response):
        loc_name = (
            response.css('.mn-event-content [itemprop="name"]::text').extract_first()
            or ""
        ).strip()
        map_link = response.css(".mn-event-maplink")
        if len(map_link) == 0:
            loc_addr_str = " ".join(
                response.css('.mn-event-content [itemprop="name"]::text').extract()[1:]
            ).strip()
            if loc_name in loc_addr_str:
                loc_name = ""
            return {
                "name": loc_name,
                "address": loc_addr_str + " Chicago, IL",
            }
        loc_street = (
            map_link.css('[itemprop="streetAddress"]::attr(content)').extract_first()
            or ""
        )
        loc_city = (
            map_link.css('[itemprop="addressLocality"]::attr(content)').extract_first()
            or "Chicago"
        )
        loc_zip = (
            map_link.css('[itemprop="postalCode"]::attr(content)').extract_first() or ""
        )
        if loc_name in loc_street:
            loc_name = ""
        return {
            "name": loc_name,
            "address": "{} {}, IL {}".format(loc_street, loc_city, loc_zip).strip(),
        }
