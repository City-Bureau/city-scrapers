from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa27Spider(CityScrapersSpider):
    name = "chi_ssa_27"
    agency = "Chicago Special Service Area #27 Lakeview West"
    timezone = "America/Chicago"
    allowed_domains = ["lakeviewchamber.com"]
    start_urls = ["https://www.lakeviewchamber.com/ssa27"]

    def parse(self, response):
        """   `parse` should always `yield` Meeting items.
        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping needs.   """
        meeting_location = ''

        for item in response.css("#content-232764 div.panel-body p"):

            if item.css("p > strong ::text").getall():
                meeting_location = self._parse_location(item)
                continue

            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=self._parse_classification(),
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="",
                location=meeting_location,
                links=self._parse_links(item),
                source=response.url,
            )
            meeting['status'] = self._get_status(meeting)
            meeting['id'] = self._get_id(meeting)
            print(str(meeting))
            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        item_txt = ''.join(item.css("p::text").getall())
        if "Annual Meeting" in item_txt:
            return "Annual Meeting"
        else:
            return COMMISSION

    def _parse_classification(self):
        # This can return COMMISSION generally or COMMITTEE for the committee meetings
        return COMMISSION

    def _parse_start(self, item):
        item_txt = item.css('a::text').get()
        if not item_txt:
            item_txt = item.css('p::text').get()

        item_txt = item_txt.replace("Annual Meeting", '').replace("Sept", 'Sep')
        p_idx = max(item_txt.find('am'), item_txt.find('pm'), 0) + 2  # so we can slice after this
        front_str = item_txt[:p_idx]  # remove comments from the rest of the string
        time_str = front_str.replace("am", "AM").replace("pm", "PM").replace('.', '')
        return datetime.strptime(time_str, '%b %d, %Y, %H:%M %p')

    def _parse_location(self, item):
        first_note = item.css("p > strong ::text").get()
        if item.css("p > strong ::text").get():
            if "Sheil Park" in first_note:
                return {
                    "address": "3505 N. Southport Ave., Chicago, IL 60657",
                    "name": "Sheil Park",
                }
            else:
                raise ValueError('Meeting address has changed')

    def _parse_links(self, item):
        if not item.css('a'):
            return []
        else:
            return [{'href': item.css('a::attr(href)').get(), 'title': 'Minutes'}]
