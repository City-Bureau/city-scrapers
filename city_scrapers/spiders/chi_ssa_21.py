import dateutil.parser
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa21Spider(CityScrapersSpider):
    name = "chi_ssa_21"
    agency = "Chicago Special Service Area #21 Lincoln Square Ravenswood"
    timezone = "America/Chicago"
    start_urls = ["http://www.lincolnsquare.org/SSA-no-21-Commission-meetings"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css(".cms-design-panel p"):
            start = self._parse_start(item)
            if not start:
                continue
            meeting = Meeting(
                title="Lincoln Square Neighborhood Improvement Program",
                description=self._parse_description(item),
                classification=COMMISSION,
                start=start,
                end=None,
                time_notes="Estimated 2 hour duration",
                all_day=False,
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_description(self, item):
        """
        Parse or generate event description.
        """
        description = ""

        # The itinerary of the meeting is always stored in the <ul>
        # element immediately following
        detail_el = item.xpath("following-sibling::*[1]")
        name = detail_el.xpath("name()").extract_first()

        if name == "ul":
            topics = list(
                map(
                    lambda topic: ": ".join(
                        filter(
                            # Remove any strings that are empty
                            None,
                            [
                                # Title of topic
                                "".join(topic.xpath("strong/text()").extract()).strip(),
                                # Detail of topic
                                "".join(topic.xpath("text()").extract()).strip(),
                            ],
                        )
                    ),
                    detail_el.xpath("li"),
                )
            )
            description = "\n".join(topics)
        return description

    def _parse_start(self, item):
        """Parse start datetime."""
        start = self._parse_date(item)
        if start:
            return start.replace(hour=9, minute=0)

    def _parse_end(self, item):
        """Parse end datetime."""
        end = self._parse_date(item)
        return end.replace(hour=11, minute=0)

    def _parse_date(self, item):
        raw_date = item.xpath("strong/text()").extract_first()
        if raw_date:
            return dateutil.parser.parse(raw_date)

    def _parse_location(self, item):
        """
        Parse or generate location. Latitude and longitude can be
        left blank and will be geocoded later.
        """
        default_loc = "Bistro Campagne, 4518 N. Lincoln Avenue"

        # If location has changed, this is where it is noted
        location = "".join(item.xpath("em//text()").extract()).strip()

        if not location:
            location = default_loc

        # Extract name of location if possible
        split_loc = location.split(",")
        address = ""
        if len(split_loc) == 2:
            address = split_loc[1].strip()
            name = split_loc[0].strip()
        else:
            address = location.strip()
            name = ""

        # Append 'Chicago, IL' if not already present
        if "chicago" not in address.lower():
            address += ", Chicago, IL"

        return {
            "address": address,
            "name": name,
        }

    def _parse_links(self, item):
        """
        Parse or generate documents.
        """
        url = item.xpath("a/@href").extract_first()
        if url:
            return [{"href": url, "title": "Minutes"}]
        return []
