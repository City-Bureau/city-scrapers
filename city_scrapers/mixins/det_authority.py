import re
from collections import defaultdict
from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting


class DetAuthorityMixin:
    """Mixin for shared behavior on Detroit public authority scrapers"""
    timezone = 'America/Detroit'
    title = 'Board of Directors'
    classification = BOARD
    location = {
        'name': 'DEGC, Guardian Building',
        'address': '500 Griswold St, Suite 2200, Detroit, MI 48226',
    }

    def parse(self, response):
        """Parse both the upcoming and previous meetings"""
        yield from self._next_meetings(response)
        yield from self._prev_meetings(response)

    def _next_meetings(self, response):
        """Parse upcoming meetings"""
        next_meeting_text = ' '.join(response.css('.content-itemContent *::text').extract())
        self._validate_location(next_meeting_text)
        self.default_start_time = self._parse_start_time(next_meeting_text)
        for meeting_start in re.findall(
            r'[a-zA-Z]{3,10}\s+\d{1,2},?\s+\d{4}.*?(?=\.)', next_meeting_text
        ):
            meeting = self._set_meeting_defaults(response)
            meeting['start'] = self._parse_start(meeting_start, self.default_start_time)
            meeting['links'] = self._parse_next_links(meeting['start'], response)
            meeting['status'] = self._get_status(meeting, text=meeting_start)
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def _prev_meetings(self, response):
        """Follow all potential previous meeting links"""
        for prev_meetings_link in response.css('a[href*="meetings/"], a[href*="minutes"]'):
            if '.pdf' in prev_meetings_link.attrib['href'].lower():
                continue
            yield response.follow(prev_meetings_link, callback=self._parse_prev_meetings)

    def _parse_prev_meetings(self, response):
        """Parse all previous meetings"""
        link_map = self._parse_prev_links(response)
        for dt, links in link_map.items():
            link_text = ' '.join(link['title'] for link in links)
            meeting = self._set_meeting_defaults(response)
            meeting['start'] = dt
            meeting['links'] = links
            meeting['title'] = self._parse_title(meeting)
            meeting['classification'] = self._parse_classification(meeting)
            meeting['status'] = self._get_status(meeting, text=link_text)
            meeting['id'] = self._get_id(meeting)
            yield meeting

    @staticmethod
    def _parse_start_time(text):
        """Parse start time from text"""
        time_str = re.search(r'\d{1,2}:\d{1,2}\s*[apmAPM\.]{2,4}', text).group()
        return datetime.strptime(re.sub(r'[\.\s]', '', time_str, flags=re.I).upper(),
                                 '%I:%M%p').time()

    @staticmethod
    def _parse_start(date_text, time_obj):
        """Parse date string and combine with start time"""
        date_str = re.search(r'\w{3,10}\s+\d{1,2},?\s+\d{4}', date_text).group().replace(',', '')
        date_obj = datetime.strptime(date_str, '%B %d %Y').date()
        return datetime.combine(date_obj, time_obj)

    def _parse_title(self, meeting):
        """Return title, included for overriding in spiders"""
        return self.title

    def _parse_classification(self, meeting):
        """Return classification, included for overriding in spiders"""
        return self.classification

    def _validate_location(self, text):
        """Check that the location hasn't changed"""
        if '500 Griswold' not in text:
            raise ValueError('Meeting location has changed')

    def _parse_next_links(self, start, response):
        """Parse links for upcoming meetings"""
        links = []
        for link in response.css('a.accordion-label'):
            link_text, link_date = self._parse_link_text_date(link)
            # Ignore if link date is None or doesn't match start date
            if start.date() != link_date:
                continue
            link_title = re.sub(
                r'\s+', ' ', re.sub(r'[a-z]{3,10}\s+\d{1,2},?\s+\d{4}', '', link_text, flags=re.I)
            ).strip()
            links.append({
                'href': response.urljoin(link.attrib['href']),
                'title': link_title,
            })
        return links

    def _parse_prev_links(self, response):
        """Parse links from previous meeting pages"""
        link_map = defaultdict(list)
        for link in response.css('li.linksGroup-item a'):
            link_text, link_date = self._parse_link_text_date(link)
            if not link_date:
                continue
            link_dt = datetime.combine(link_date, self.default_start_time)
            link_title = re.sub(
                r'\s+', ' ', re.sub(r'[a-z]{3,10}\s+\d{1,2},?\s+\d{4}', '', link_text, flags=re.I)
            ).strip()
            link_map[link_dt].append({
                'href': response.urljoin(link.attrib['href']),
                'title': link_title,
            })
        return link_map

    def _parse_link_text_date(self, link):
        """Parse the text of a link as well as the date (if available)"""
        link_text = ' '.join(link.css('*::text').extract()).strip()
        link_date_match = re.search(r'[a-z]{3,10}\s+\d{1,2},?\s+\d{4}', link_text, flags=re.I)
        if not link_date_match:
            return link_text, None
        link_date_str = link_date_match.group().replace(',', '')
        link_date = datetime.strptime(link_date_str, '%B %d %Y').date()
        return link_text, link_date

    def _set_meeting_defaults(self, response):
        """Return default meeting object"""
        return Meeting(
            title=self.title,
            description='',
            classification=self.classification,
            end=None,
            time_notes="See source to confirm meeting time",
            all_day=False,
            location=self.location,
            links=[],
            source=response.url,
        )
