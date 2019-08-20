import re
from datetime import datetime, time

import dateutil.parser
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class IlLotterySpider(CityScrapersSpider):
    name = "il_lottery"
    agency = "Illinois Lottery Control Board"
    timezone = "America/Chicago"
    allowed_domains = ["www.illinoislottery.com"]
    start_urls = ["https://www.illinoislottery.com/illinois-lottery/lottery-control-board/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """

        if re.search(r'122 South Michigan Avenue, 19th Floor', response.text) is None:
            raise ValueError('Meeting address has changed')

        meetings = self._parse_upcoming(response)

        for item in meetings:
            meeting = Meeting(
                title=self._parse_title(item),
                description='',
                classification=BOARD,
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes='',
                location={
                    'name': 'Chicago Lottery Office',
                    'address': '122 South Michigan Avenue, 19th Floor, Chicago, IL 60603'
                },
                source=response.url,
            )
            meeting['id'] = self._get_id(meeting)
            meeting['status'] = self._get_status(meeting, text=item)
            meeting['links'] = self._parse_agenda_links(response, date=meeting['start'].date())

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        suffix = ''
        if 'QTR' in item:
            suffix = " Quarterly Meeting"
        elif 'Special' in item:
            suffix = ' Special Meeting'
        return "Lottery Control Board{}".format(suffix)

    @staticmethod
    def parse_time(source):
        """Returns times given string with format h:mm am|pm"""
        time_regex = re.compile(r'([1-9]):([0-5][0-9])\s?(am|pm)')
        hour, minute, period = time_regex.search(source).groups()

        hour = int(hour)
        minute = int(minute)
        if (period == 'pm') and (hour != 12):
            hour += 12
        return time(hour, minute)

    @staticmethod
    def parse_day(source):
        """Returns date"""
        # search for dates with '/' (ex: 08/16/19)
        if "/" in source:
            m = re.search(
                r'.+[,-]\s(?P<month>\d{2})\/(?P<day>\d{2})\/(?P<year>\d{2})\s.+', source.strip()
            )
        # search for date in format "[month] [dd], [yyyy]" (ex: 'May 15, 2019')
        else:
            m = re.search(
                r'.+[,-]\s*(?P<month>[A-Za-z]+)\s(?P<day>\d{1,2}),\s(?P<year>\d{4}).*',
                source.strip()
            )

        dt = dateutil.parser.parse(
            '{mo} {day} {year}'.format(
                mo=m.group('month'), day=m.group('day'), year=m.group('year')
            )
        )
        return dt.date()

    def _parse_start(self, item):
        """Parse start date and time."""
        return datetime.combine(self.parse_day(item), self.parse_time(item))

    def _parse_upcoming(self, response):
        """Returns a list of lines with dates following the string 'Upcoming Meeting Dates' """

        meeting_xpath = '//p[contains(., "Upcoming meeting dates")]'

        # future meetings are separated by <br> tags
        meeting_lines = response.xpath(meeting_xpath).css('p').get().split("<br>")

        # only keep <br> lines that include a weekday
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        meeting_lines = [x for x in meeting_lines if any(weekday in x for weekday in weekdays)]

        return meeting_lines

    def _parse_agenda_links(self, response, date):
        '''
        Extracts link to agenda for a specific meeting date
        Args:
            date: A datetime object with the date of the desired agenda
        Return:
            List of dictionaries with the keys title (title/description of the link)
            and href (link URL) for the agenda for the meeting on the requested date
        '''
        agenda_links = []
        for link in response.xpath('//p//a'):
            link_text_selector = link.xpath('text()')
            if link_text_selector:
                link_text = link_text_selector.get()
                if 'Agenda' in link_text:
                    agenda_date = self.parse_day(link_text)
                    if agenda_date == date:
                        link_href = link.xpath('@href').get()
                        agenda_links = [{
                            "href": 'https://www.illinoislottery.com{}'.format(link_href),
                            "title": link_text.replace(u'\xa0', u' ')
                        }]

        return agenda_links
