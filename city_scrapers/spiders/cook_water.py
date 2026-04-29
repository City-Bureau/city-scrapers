from collections import defaultdict
from datetime import datetime, timedelta

from city_scrapers_core.constants import BOARD, COMMITTEE, FORUM
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import LegistarSpider


class CookWaterSpider(LegistarSpider):
    name = "cook_water"
    agency = "Metropolitan Water Reclamation District of Greater Chicago"
    event_timezone = "America/Chicago"
    start_urls = ["https://mwrd.legistar.com/Calendar.aspx"]
    location = {
        "name": "Board Room",
        "address": "100 East Erie Street Chicago, IL 60611",
    }
    link_types = ["Meeting Details", "Accessible Agenda", "Accessible Minutes"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.since_year = 2020
        self.legistar_keys = set()

    def parse_legistar(self, events):
        three_months_ago = datetime.today() - timedelta(days=90)
        for event in events:
            title = self._parse_title(event)
            start = self.legistar_start(event)
            if (
                title == "Study Session"
                or not start
                or (
                    start < three_months_ago
                    and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE")
                )
            ):
                continue
            meeting = Meeting(
                title=title,
                description="",
                classification=self._parse_classification(title),
                start=start,
                end=None,
                time_notes="",
                all_day=False,
                location=self.location,
                links=self.legistar_links(event),
                source=self.legistar_source(event),
            )
            meeting["status"] = self._get_status(meeting, event["Meeting Location"])
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_legistar_events(self, response):
        events_table = response.css("table.rgMasterTable")[0]

        headers = []
        for header in events_table.css("th[class^='rgHeader']"):
            header_text = (
                " ".join(header.css("*::text").extract()).replace("&nbsp;", " ").strip()
            )
            header_inputs = header.css("input")
            if header_text:
                headers.append(header_text)
            elif len(header_inputs) > 0:
                headers.append(header_inputs[0].attrib["value"])
            else:
                headers.append(header.css("img")[0].attrib["alt"])

        events = []
        for row in events_table.css("tr.rgRow, tr.rgAltRow"):
            try:
                data = defaultdict(lambda: None)
                for header, field in zip(headers, row.css("td")):
                    field_text = (
                        " ".join(field.css("*::text").extract())
                        .replace("&nbsp;", " ")
                        .strip()
                    )
                    url = None
                    if len(field.css("a")) > 0:
                        link_el = field.css("a")[0]
                        if "onclick" in link_el.attrib and link_el.attrib[
                            "onclick"
                        ].startswith(("radopen('", "window.open", "OpenTelerikWindow")):
                            url = response.urljoin(
                                link_el.attrib["onclick"].split("'")[1]
                            )
                        elif "href" in link_el.attrib:
                            url = response.urljoin(link_el.attrib["href"])
                    if url:
                        # Detect iCal by URL pattern, not header name
                        if "View.ashx?M=IC" in url:
                            header = "iCalendar"
                            value = {"url": url}
                        else:
                            value = {"label": field_text, "url": url}
                    else:
                        value = field_text

                    data[header] = value

                ical_url = data.get("iCalendar", {}).get("url")
                if ical_url is None or ical_url in self._scraped_urls:
                    continue
                else:
                    self._scraped_urls.add(ical_url)
                events.append(dict(data))
            except Exception:
                pass

        return events

    def _parse_classification(self, name):
        """
        Parse or generate classification (e.g. town hall).
        """
        if "committee" in name.lower():
            return COMMITTEE
        if "hearing" in name.lower():
            return FORUM
        return BOARD

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item["Name"]["label"]
