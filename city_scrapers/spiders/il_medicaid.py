import scrapy
from city_scrapers_core.constants import ADVISORY_COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from datetime import datetime

class IlMedicaidSpider(CityScrapersSpider):
    name = "il_medicaid"
    agency = "Illinois Medical Adivsory Committee"
    timezone = "America/Chicago"
    allowed_domains = ["www.illinois.gov"]

    # Using the MAC main page makes it more convenient to grab the meeting
    # title
    start_urls = ["https://www.illinois.gov/hfs/About/BoardsandCommisions/MAC/Pages/"
                  "default.aspx"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        # The title of the main of the committee/subcommittee page is the name
        # of the said committee/subcommittee.
        title = self._parse_title(response.xpath("//title/text()").get())

        # The meeting times are listed in the "Schedules" page for each
        # committee/subcommittee.

        schedule_xpath = "//a[descendant::*[contains(text(),'chedule')]]/@href"
        schedule_page_url = response.xpath(schedule_xpath).get()
        if schedule_page_url is not None:
            schedule_page_url = response.urljoin(schedule_page_url)
            request = scrapy.Request(url = schedule_page_url,
                                     callback = self._get_meetings)
            request.meta['title'] = title
            yield request

        # Request subcommittee pages.

        subcom_xpath = "//a[contains(@title, 'ubcommitt')]/following-sibling::ul/li/a/@href"
        subcom_pages = response.xpath(subcom_xpath).getall()
        if subcom_pages is not None:
            for subcom in subcom_pages:
                subcom = response.urljoin(subcom)
                yield scrapy.Request(url=subcom, callback=self.parse)

        # TBD: Request minutes and notices

    # Just stripping the white spaces seems enough 
    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item.strip()

    def _get_meetings(self, response):
        """
        Callback method for scraping the 'schedule' pages.
        """
        date_xpath = "//h2[contains(text(),'Meeting Dates')]/following::ul/li/p/text()"
        for date_str in response.xpath(date_xpath).re(r'[\w]+[\s]+[\d]+,\s[\d]+'):
            date = self._parse_date(date_str)

            meeting = Meeting(
                title= response.meta['title'],
                description='', # TBD
                classification=ADVISORY_COMMITTEE, # TBD
                start= date.replace(hour=10),# TBD
                end= date.replace(hour=12),# TBD
                all_day=False,# TBD
                time_notes="",# TBD
                location={# TBD
                    'name': 'James R. Thompson Center',
                    'address': '100 W Randolph St, 2nd flr. Rm. 2025, Chicago, IL 60601',
                },
                links=[],# TBD
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_date(self, date):
        """
        Parses meeting date.
        """
        date = date.replace('\xa0',' ')

        try:
            return datetime.strptime(date, "%B %d, %Y")
        except ValueError:
            return datetime(1900,1,1)

    # def _parse_description(self, item):
    #     """Parse or generate meeting description."""
    #     return ""

    # def _parse_classification(self, item):
    #     """Parse or generate classification from allowed options."""
    #     return NOT_CLASSIFIED

    # def _parse_start(self, item):
    #     """Parse start datetime as a naive datetime object."""
    #     return None

    # def _parse_end(self, item):
    #     """Parse end datetime as a naive datetime object. Added by pipeline if None"""
    #     return None

    # def _parse_time_notes(self, item):
    #     """Parse any additional notes on the timing of the meeting"""
    #     return ""

    # def _parse_all_day(self, item):
    #     """Parse or generate all-day status. Defaults to False."""
    #     return False

    # def _parse_location(self, item):
    #     """Parse or generate location."""
    #     return {
    #         "address": "",
    #         "name": "",
    #     }

    # def _parse_links(self, item):
    #     """Parse or generate links."""
    #     return [{"href": "", "title": ""}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
