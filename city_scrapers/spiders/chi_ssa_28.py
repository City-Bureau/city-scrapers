from datetime import datetime

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa28Spider(CityScrapersSpider):
    name = "chi_ssa_28"
    agency = "Chicago Special Service Area #28 Six Corners"
    timezone = "America/Chicago"
    start_urls = ["https://sixcorners.com/ssa28"]
    location = {
        "name": "Portage Arts Lofts",
        "address": "4041 N. Milwaukee Ave. #302, Chicago, IL 60641"
    }

    def parse(self, response):
        """Since the meeting dates are in an unordered text block, we'll need to parse
        them outside of the main parsing loop, and use the list index to iterate through
        xpath for things like links.
        """
        dates = response.xpath('//div[@class="col sqs-col-3 span-3"]/div/div/p[2]/text()').getall()
        dates = [d.strip(', ')[:-2] for d in dates]
        dates = [d for d in dates if d]
        self._validate_location(response)
        for date in dates:
            item = response.xpath('//div[@class="col sqs-col-3 span-3"]/div/div/p[2]')
            meeting = Meeting(
                title="Six Corners Commission",
                description="",
                classification=self._parse_classification(date),
                start=self._parse_start(item, date),
                end=None,
                all_day=self._parse_all_day(date),
                time_notes="",
                location=self.location,
                links=self._parse_links(item, date, dates, response),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting, text=date)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _validate_location(self, response):
        if "4041 N" not in response.xpath(
            '//div[@class="col sqs-col-3 span-3"]/div/div/p[1]/em/text()'
        ).get():
            raise ValueError("Meeting location has changed")

    def _parse_classification(self, date):
        """Parse or generate classification from allowed options."""
        return COMMISSION

    def _parse_start(self, item, date):
        """Parse start datetime as a naive datetime object."""
        start_year = item.xpath('.//strong/text()').get()
        start_date = date
        start_time = "1:30 PM"
        start = datetime.strptime(start_date + start_year + start_time, "%B %d%Y%H:%M %p")
        return start

    def _parse_all_day(self, date):
        """Parse or generate all-day status. Defaults to False."""
        return False

    def _parse_links(self, item, date, dates, response):
        """Parse or generate links. Uses the index from the dates list."""
        links = []
        if dates.index(date) == 0:
            start_node = 1 + dates.index(date)
            stop_node = 2 + dates.index(date)
        else:
            start_node = 1 + dates.index(date) + dates.index(date)
            stop_node = 2 + dates.index(date) + dates.index(date)
        selector_path = './/a[$i]'
        hrefs = [item.xpath(selector_path, i=start_node), item.xpath(selector_path, i=stop_node)]
        for href in hrefs:
            if href:
                links.append({
                    "title": href.xpath('.//text()').get(),
                    "href": response.urljoin(href.xpath('.//@href').get())
                })
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
