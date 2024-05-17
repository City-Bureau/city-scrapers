from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as date_parse


class ChiHumanRelationsSpider(CityScrapersSpider):
    name = "chi_human_relations"
    agency = "Chicago Commission on Human Relations"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.chicago.gov/city/en/depts/cchr/supp_info/BoardMeetingInformation.html"  # noqa
    ]
    title = "Chicago Commission on Human Relations Board Meeting"
    location = {
        "name": "Chicago Commission on Human Relations - board room",
        "address": "740 N Sedgwick St, 4th Floor Boardroom, Chicago, IL 60654",
    }
    links = [
        {
            "title": "Meeting materials",
            "href": "https://www.chicago.gov/city/en/depts/cchr/supp_info/BoardMeetingInformation.html",  # noqa
        }
    ]

    def parse(self, response):
        for header in response.css("h5 strong"):
            text = header.xpath("string()").get().strip()
            if "next meeting" in text:
                date_str = text.split("scheduled for")[-1].strip()
                start = self._parse_start(date_str)
                meeting = Meeting(
                    title=self.title,
                    description="",
                    classification=COMMISSION,
                    start=start,
                    end=None,
                    all_day=False,
                    time_notes="",
                    location=self.location,
                    links=self.links,
                    source=response.url,
                )
                # we provide additional text to _get_status to help determine
                # if the meeting is cancelled or not
                meeting["status"] = self._get_status(meeting, text=text)
                meeting["id"] = self._get_id(meeting)
                yield meeting

    def _parse_start(self, text):
        """
        Expecting text like:
        'The next meeting of the Chicago Commission on Human Relations is
        scheduled for Thursday, May 9 at 9:30 a.m'
        Parse the date and time from the text
        """
        if "scheduled for" not in text:
            self.logger.error(
                "Could not find 'scheduled for' in text – text format may have changed"  # noqa
            )
        date_str = text.split("scheduled for")[-1].strip()
        return date_parse(date_str)
