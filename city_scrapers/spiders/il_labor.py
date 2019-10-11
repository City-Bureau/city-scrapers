from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse


class IlLaborSpider(CityScrapersSpider):
    name = 'il_labor'
    agency = 'Illinois Labor Relations Board'
    start_urls = ['https://www2.illinois.gov/ilrb/meetings/Pages/default.aspx']
    event_timezone = 'America/Chicago'
    """
    This page only lists the next upcoming meeting for each of the three boards.
    All other meetingd dates are `proposed` and only available via PDF.
    """
    def parse(self, response):
        for item in response.css('.soi-article-content .container > .row > p'):
            """
            Some monthly meetings are skipped. Instead of providing a date,
            there's text that says 'No /name/ meeting in month'.
            If the date/time info can't be parsed, assume that it is a `no meeting`
            notice.
            """
            start = self._parse_start(item)
            if start is None:
                continue
            title = self._parse_title(item)
            meeting = Meeting(
                title=title,
                description=self._parse_description(response),
                classification=BOARD,
                start=start,
                end=None,
                time_notes='',
                all_day=False,
                location=self._parse_location(item),
                links=self._parse_links(item, response),
                source=response.url,
            )
            meeting['id'] = self._get_id(meeting)
            meeting['status'] = self._get_status(meeting)
            yield meeting

    def _parse_location(self, item):
        """
        Get address from the next paragraph following the event item.
        Note: the structure of the page is not consistent. Usually the
        next row contains the meeting time, but sometimes
        multiple meeting locations are listed within a single div.
        """
        addr_in_row = item.xpath('following-sibling::*//p//text()')
        addr_next_row = item.xpath('../following-sibling::div[1]//p//text()')
        address_list = addr_in_row if len(addr_in_row) > 0 else addr_next_row
        chi_address_list = [
            addr.replace('\xa0', '').strip()
            for addr in address_list.extract()
            if 'chicago' in addr.lower()
        ]
        return {'address': chi_address_list[0], 'name': ''}

    def _parse_title(self, item):
        """
        Get meeting title from the first `<strong>`.
        """
        name = item.css('a::text').extract_first()
        if name:
            return name.title()
        return item.css('strong::text').extract_first().title()

    def _parse_description(self, response):
        """
        No meeting-specific description, so use a generic description from page.
        """
        return response.css('#ctl00_PlaceHolderMain_ctl01__ControlWrapper_RichHtmlField p::text'
                            ).extract_first().strip()

    def _parse_start(self, item):
        """
        Parse start date and time from the second `<strong>`
        """
        try:
            dt_str = item.css('strong:nth-of-type(2)::text').extract_first()
            if not dt_str:
                dt_str = item.css('strong:nth-of-type(3)::text').extract_first()
            return parse(dt_str or '')
        except ValueError:
            return None

    def _parse_links(self, item, response):
        href = item.css('a::attr(href)').extract_first()
        if href:
            return [{'href': response.urljoin(href), 'title': 'Agenda'}]
        return []
