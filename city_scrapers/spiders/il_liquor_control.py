import datetime
import requests

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlLiquorControlSpider(CityScrapersSpider):
    name = "il_liquor_control"
    agency = "Illinois Liquor Control Commission"
    timezone = "America/Chicago"
    allowed_domains = ["www2.illinois.gov"]
    start_urls = [
        "https://www2.illinois.gov/ilcc/Divisions/Pages/Legal/"
        "Hearing-Schedule-for-Chicago-IL-and-Springfield-IL.aspx",
        "https://www2.illinois.gov/ilcc/Divisions/Pages/Legal/Meeting-minutes.aspx"
    ]  # start_urls[0] contains links future meetings. start_urls[1] contains past
    # meeting minutes links

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.
        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping

        Each tentative meeting has own page. start_urls[0] is only used to get links for the pages.
        The links are sent to _next_meeting.

        start_urls[1] is for obtaining datetime info for past meetings. Then checks if
        meeting detail page is still valid. If valid scrape through _prev_meeting_w_page. If not
        valid, scrape available info from _prev_meeting_wo_page.
        """

        if response.url == self.start_urls[0]:
            for future_meeting_href in response.css('div.soi-link-item a::attr(href)').extract():
                yield response.follow(future_meeting_href, callback=self._next_meeting)

        if response.url == self.start_urls[1]:
            for idx, past_meeting_date in enumerate(response.css("div.link-item ::text").extract()):
                dt_object = datetime.datetime.strptime(past_meeting_date, "%B %d, %Y Minutes")
                minute_href = response.css("div.link-item a::attr(href)").extract()[idx]
                meeting_url = ("https://www2.illinois.gov/ilcc/Events/Pages/Board-"
                               "Meeting-{0}-{1}-{2:%y}.aspx".format(
                                dt_object.month, dt_object.day, dt_object))
                if requests.get(meeting_url).status_code == 200:
                    yield response.follow(meeting_url,
                                          callback=self._prev_meeting_w_page,
                                          cb_kwargs=dict(minute_href=minute_href))
                else:
                    yield from self._prev_meeting_wo_page(response, dt_object, minute_href)

    def _next_meeting(self, response):
        dt_str = ' '.join([
                x.strip() for x in response.css('div.soi-event-data::text').extract()
            ])  # Extract string that contains datetime info.
        meeting = Meeting(
                title=self._parse_title(response),
                description='',
                classification=BOARD,
                start=self._parse_start(dt_str),
                end=self._parse_end(dt_str),
                all_day=False,
                time_notes='',
                location=self._parse_location(response),
                links=self._parse_link(response, self._parse_start(dt_str), None),
                source=response.url,
            )

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _prev_meeting_w_page(self, response, minute_href):
        dt_str = ' '.join([
                x.strip() for x in response.css('div.soi-event-data::text').extract()
            ])
        meeting = Meeting(
                title=self._parse_title(response),
                description='',
                classification=BOARD,
                start=self._parse_start(dt_str),
                end=self._parse_end(dt_str),
                all_day=False,
                time_notes='',
                location=self._parse_location(response),
                links=self._parse_link(
                        response, self._parse_start(dt_str), minute_href),
                source=response.url,
                )

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _prev_meeting_wo_page(self, response, dt_object, minute_href):
        meeting = Meeting(
                title='Board Meeting',
                description='',
                classification=BOARD,
                start=dt_object + datetime.timedelta(hours=13),
                end=dt_object + datetime.timedelta(hours=16),
                all_day=False,
                time_notes='Meeting time is estimated.',
                location={'address': '100 West Randolph 9-040 Chicago, IL', 'name': ''},
                links=self._parse_link(
                        response, dt_object, minute_href),
                source=minute_href,
                )

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _parse_title(self, response):
        """Parse or generate meeting title."""
        return response.css('p.soi-eventType::text').extract_first().strip()

    def _parse_start(self, dt_str):
        """Parse start datetime as a naive datetime object."""

        return datetime.datetime.strptime(' '.join(dt_str.split()[:6]), '%A, %B %d, %Y %I:%M %p')

    def _parse_end(self, dt_str):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return datetime.datetime.strptime(
            ' '.join(dt_str.split()[:4] + dt_str.split()[7:]), '%A, %B %d, %Y %I:%M %p')

    def _parse_location(self, response):
        """Parse or generate location."""
        loc_str = ' '.join([
                x.strip() for x in response.css('div.soi-eventlocation div::text').extract()
            ])
        return {"address": '{} Chicago, IL'.format(' '.join(loc_str.split()[:4])),
                "name": "", }

    def _parse_link(self, response, dt_object, minute_href):
        """Use agenda_href if it is found from detail page. If not, try href using formatting
        datetime. """
        links = []
        agenda_href = response.css("div.item.link-item.bullet a::attr(href)").extract()
        hidden_agenda_href = ("https://www2.illinois.gov/ilcc/Events/EventDocuments/{0.month}"
                              "-{0.day}-{0.year}%20ILCC%20Agenda.pdf".format(dt_object))
        if agenda_href:
            links.append({
                    'title': 'Agenda',
                    'href': agenda_href[0]
                    })
        elif requests.get(hidden_agenda_href).status_code == 200:
            links.append({
                        'title': 'Agenda',
                        'href': hidden_agenda_href
                        })
        if minute_href:
            links.append({
                'title': 'Minutes',
                'href': minute_href
                })
        return links
