import re
from datetime import datetime, timedelta

from city_scrapers_core.constants import NOT_CLASSIFIED, CANCELLED, PASSED
from city_scrapers_core.constants import TENTATIVE, COMMITTEE, COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy import Request


class ChiOhareNoiseSpider(CityScrapersSpider):
    name = "chi_ohare_noise"
    agency = "Chicago O'Hare Noise Compatibility Commission"
    timezone = "America/Chicago"

    class ChiOhareNoiseSubSpider1:
        def parse(self, response):
            """
            `parse` should always `yield` Meeting items.

            Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
            needs.
            """
            for item in response.css(".ev_td_li"):
                surl = self._parse_url(item)
                yield Request(url=response.urljoin(surl), callback=self._parse_details)

            next_page = response.xpath("//div[@class='previousmonth']/a/@href").get()
            if next_page is not None:
                yield response.follow(response.urljoin(next_page), callback=self.parse)

        def _parse_details(self, response):
            stime = self._parse_start(response)
            meeting = Meeting(
                title=self._parse_title(response).replace('CANCELLED ', '').strip('- '),
                description=self._parse_description(response),
                start=stime,
                end=stime + timedelta(hours=1),
                all_day=False,
                location=self._parse_location(response),
                links=self._parse_links(response),
                source=response.url,
            )

            meeting = self._get_status(meeting)
            meeting = self._parse_classification(meeting)
            return meeting

        def _parse_title(self, response):
            """Parse or generate meeting title."""
            return response.xpath(
                "//div[@class='jev_evdt_header']/div/h2/text()"
            ).extract()[0]

        def _parse_url(self, response):
            """Parse or generate meeting title."""
            return [i.strip() for i in response.xpath("p/a/@href").extract()][0]

        def _parse_description(self, response):
            """Parse or generate meeting description."""
            return response.xpath("//div[@class='jev_evdt_desc']/p/text()").get() or ""

        def _parse_classification(self, meeting):
            """Parse or generate classification from allowed options."""
            if 'committee' in meeting['title'].lower():
                meeting['classification'] = COMMITTEE
            elif 'commission' in meeting['title'].lower():
                meeting['classification'] = COMMISSION
            else:
                meeting['classification'] = NOT_CLASSIFIED
            return meeting

        def _parse_start(self, response):
            """Parse start datetime as a naive datetime object."""
            return datetime.strptime(
                " ".join(
                    [
                        i.strip()
                        for i in response.xpath(
                            "//div[@class='jev_evdt_header']/div/p/text()"
                        ).extract()
                    ]
                ),
                "%A, %B %d, %Y %I:%M%p",
            )

        def _parse_all_day(self, response):
            """Parse or generate all-day status. Defaults to False."""
            return False

        def _parse_location(self, response):
            """Parse or generate location."""
            addr = re.split(
                "-|,",
                response.xpath("//div[@class='jev_evdt_location']/text()")
                .extract()[0]
                .strip(),
                maxsplit=1,
            )
            return {
                # Using reverse indexing for the cases
                # where there is no building name or no location
                "address": addr[-1].strip(),
                "name": addr[0].strip(),
            }

        def _parse_links(self, response):
            """Parse or generate links."""
            return [
                {"href": item, "title": "Zoom Link"}
                for item in response.xpath(
                    "//div[@class='jev_evdt_desc']/p/a/@href"
                ).extract()[:1]
            ]

        def _parse_source(self, response):
            """Parse or generate source."""
            return response.url
        
        def _get_status(self, meeting):
            if 'cancelled' in meeting['title'].lower():
                meeting['status'] = CANCELLED
            elif datetime.now() > meeting['end']:
                meeting['status'] = PASSED
            else:
                meeting['status'] = TENTATIVE

            return meeting

    class ChiOhareNoiseSubSpider2:
        def parse(self, response):
            """
            `parse` should always `yield` Meeting items.

            Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
            needs.
            """
            for item in response.css("tr.cat-list-row0") + response.css(
                "tr.cat-list-row1"
            ):
                meeting = Meeting(
                    title=self._parse_title(item),
                    start=self._parse_start(item),
                    links=self._parse_links(item, response),
                    source=self._parse_source(response),
                )

                meeting = self._get_status(meeting)
                meeting = self._parse_classification(meeting)
                yield meeting
            next_page = response.xpath("//li[@class='pagination-next']/a/@href").get()
            if next_page is not None:
                yield response.follow(response.urljoin(next_page), callback=self.parse)

        def _parse_title(self, item):
            """Parse or generate meeting title."""
            return item.css(".djc_category span").xpath("text()").extract()[0]

        def _parse_start(self, item):
            """Parse start datetime as a naive datetime object."""
            return datetime.strptime(
                item.css(".djc_producer span").xpath("text()").extract()[0], "%B %d, %Y"
            )

        def _parse_links(self, item, response):
            """Parse or generate links."""
            links = item.xpath('td[@class="djc_price"]/div/ul/li/a')
            return [
                {
                    "href": response.url
                    + "?"
                    + link.xpath("@href").extract()[0].split("?")[1],
                    "title": link.xpath("span/text()").extract()[0],
                }
                for link in links
            ]

        def _parse_source(self, response):
            """Parse or generate source."""
            return response.url

        def _get_status(self, meeting):
            if 'cancelled' in meeting['title'].lower():
                meeting['status'] = CANCELLED
            elif datetime.now() > meeting['start']:
                meeting['status'] = PASSED
            else:
                meeting['status'] = TENTATIVE

            return meeting

        def _parse_classification(self, meeting):
            """Parse or generate classification from allowed options."""
            if 'committee' in meeting['title'].lower():
                meeting['classification'] = COMMITTEE
            elif 'commission' in meeting['title'].lower():
                meeting['classification'] = COMMISSION
            else:
                meeting['classification'] = NOT_CLASSIFIED
            return meeting

    def start_requests(self):
        urls = [
            "https://www.oharenoise.org/meetings-all/year.listevents/",
            "https://www.oharenoise.org/about-oncc/agendas-and-minutes",
        ]
        yield Request(urls[0], callback=self.ChiOhareNoiseSubSpider1().parse)
        yield Request(urls[1], callback=self.ChiOhareNoiseSubSpider2().parse)
