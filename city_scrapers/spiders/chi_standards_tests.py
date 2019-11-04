import datetime

from city_scrapers_core.constants import COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiStandardsTestsSpider(CityScrapersSpider):
    name = "chi_standards_tests"
    agency = "Chicago Committee on Standards and Tests"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.chicago.gov/city/en/depts/bldgs/supp_info/committee_on_standardsandtests.html"
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.
        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.xpath("//div[@class='col-xs-12']/table[1]//td/p"):
            if self._pass_filter(item) is False:
                continue
            meeting = Meeting(
                title="Committee on Standards and Tests",
                description="",
                classification=COMMITTEE,
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes=
                "Meetings are scheduled by appointments and, thus, may not take place. Confirm details with the agency",
                location={
                    "address": "121 North LaSalle Street, Room 906, Chicago, Illinois 60602",
                    "name": "City Hall"
                },
                links=self._parse_links(item),
                source=response.url,
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _pass_filter(self, item):
        # If no meeting
        if item.xpath('.//em/text()').get() == 'no meeting':
            return False

        # Check if date string
        months = [
            'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
        ]
        date_str = item.xpath('.//text()').get()
        if any(date_str.lower().startswith(month) for month in months):
            return True
        else:
            return False

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        year = item.xpath(".//../../../../../p[1]/strong/text()").get()
        year = year.split()[0]
        month_day = item.xpath(".//text()").get()
        if month_day.startswith('Feb'):
            # February has typo on website
            month_day = month_day.replace('Feburary', 'February')
        date = year + ' ' + month_day

        date_obj = datetime.datetime.strptime(date, '%Y %B %d')
        time_obj = datetime.time(13, 30, 0)
        return datetime.datetime.combine(date_obj, time_obj)

    def _parse_links(self, item):
        """Parse or generate links."""
        links = []
        a_tag = item.xpath('.//a')
        if a_tag:
            href = 'chicago.gov' + a_tag.xpath('.//@href').get()
            title = a_tag.xpath('.//text()').get()
            links.append({
                "href": 'chicago.gov' + a_tag.xpath('.//@href').get(),
                "title": a_tag.xpath('.//text()').get(),
            })
        return links
