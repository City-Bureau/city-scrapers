import logging
import re
import unicodedata
from datetime import datetime, timedelta

from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ChiSsa23Spider(CityScrapersSpider):
    name = "chi_ssa_23"
    agency = "Chicago Special Service Area #23 Clark Street"
    timezone = "America/Chicago"
    start_urls = ["https://www.lincolnparkchamber.com/clark-street-ssa-administration/"]
    location = {
        "name": "Lincoln Park Chamber of Commerce",
        "address": "2468 N. Lincoln Chicago, IL 60614"
    }
    # Each meeting takes place on Wednesday 4 PM
    meeting_day = 'Wednesday'
    time = '4 pm'

    def parse(self, response):
        # Due to the current lack of documents for the meetings of 2020
        # no assumption is made regarding the expected HTML page format
        # once these are uploaded. 
        h4s = response.xpath('//h4')
        meeting_years = list()

        for entry in h4s.xpath('./text()').getall():
            # Do not allow duplicates
            if entry[0:4] not in meeting_years:
                meeting_years.append(entry[0:4])

        # General meeting description is mentioned just after the H4 for the current year
        general_desc = h4s.xpath('following-sibling::p[1]//em//text()').extract_first()

        # List containing all meeting dictionaries
        meetings = list()

        link_collection = []
        for h4 in h4s[1:]:
            # Get the links for each meeting
            link_collection.append(h4.xpath('following-sibling::p[1]//a'))

        last_year = datetime.today().replace(year=datetime.today().year - 1)

        for year_counter, year in enumerate(meeting_years):

            if year_counter == 0:
                for item in h4s.xpath('following-sibling::ol[1]//li//text()').extract():
                    start, end = self._parse_start_end(item, meeting_years[0])

                    meetings.append({
                        'start': start,
                        'end': end,
                        # Currently no meetings from 2020 have links
                        'links': None
                    })

            # Always multiply the counter with two as each year has usually two links
            else:
                logging.log(logging.DEBUG, link_collection[year_counter])
                for item_counter, item in enumerate(link_collection[2 * (year_counter - 1)]):
                    # Get the text part
                    item_str = item.xpath('./text()').extract_first()
                    logging.log(logging.DEBUG, item_str)
                    start, end = self._parse_start_end(item_str, year)

                    links = [item.xpath('@href').extract_first()]
                    # Try to see if we have a second link
                    try:
                        links.append(
                            link_collection[2 * (year_counter - 1) +
                                            1][item_counter].xpath('@href').extract_first()
                        )
                    except IndexError:
                        # No problem, this means that this is an older entry and
                        # there is no second link to this element
                        links.append(None)
                    # check for old entries
                    if start < last_year and not self.settings.getbool("CITY_SCRAPERS_ARCHIVE"):
                        continue
                    meetings.append({'start': start, 'end': end, 'links': self._parse_links(links)})

        # Create the meeting objects
        for item in meetings:

            meeting = Meeting(
                title='Commission',
                description=unicodedata.normalize("NFKD", general_desc),
                classification=COMMISSION,
                start=item['start'],
                end=item['end'],
                time_notes='Estimated 90 minutes duration',
                all_day=False,
                location=self.location,
                links=item['links'],
                source=response.url,
            )

            meeting['status'] = self._get_status(meeting)
            meeting['id'] = self._get_id(meeting)
            yield meeting

    def _parse_start_end(self, item, year):
        """
        Parse start date and time.
        """

        # Split the month day string and make sure to drop the year before that
        dm_str = item.split(',')[0].split()

        # Adding a 0 as padding for single-digit days
        if len(dm_str[1]) < 2:
            dm_str[1] = '0' + dm_str[1]
        dt_str = dm_str[0] + ' ' + dm_str[1]

        start = datetime.strptime(
            '{} {} {} {}'.format(self.meeting_day, re.sub(r'[,\.]', '', dt_str), self.time, year),
            '%A %B %d %I %p %Y'
        )
        end = start + timedelta(minutes=90)

        return start, end

    def _parse_links(self, items):
        documents = []
        logging.log(logging.DEBUG, items)
        for url in items:
            if url:
                documents.append(self._build_link_dict(url))

        return documents

    def _build_link_dict(self, url):
        if 'agenda' in url.lower():
            return {'href': url, 'title': 'Agenda'}
        elif 'minutes' in url.lower():
            return {'href': url, 'title': 'Minutes'}
        else:
            return {'href': url, 'title': 'Link'}
