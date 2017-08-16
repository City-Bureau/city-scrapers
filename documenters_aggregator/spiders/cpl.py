# -*- coding: utf-8 -*-
"""
All spiders should yield data shaped according to the Open Civic Data
specification (http://docs.opencivicdata.org/en/latest/data/event.html).
"""
import scrapy
import re

from datetime import datetime

"""
PROJECT STATUS AS OF 7/15/17 AT 7:15PM:
    Currently have all the data on https://www.chipublib.org/board-of-directors/board-meeting-schedule/
    loading with each event as a string. Now need to parse out the random characters from
    each line in the event string, turn the date into the open civic data format date, and
    then do a few other project reqs (for example make ID) to get the data in the right 
    format before this spider is declared complete!!!

    SETUP:
        workon documentors_aggregator
        scrapy shell https://www.chipublib.org/board-of-directors/board-meeting-schedule/
            (may need to comment out some random code below to get the interactive
            shell running)
        and then you can work on it!!! woohoo
"""

class CplSpider(scrapy.Spider):
    name = 'cpl'
    allowed_domains = ['https://www.chipublib.org/']
    start_urls = ['https://www.chipublib.org/board-of-directors/board-meeting-schedule/']

    #extracts each <P> event as a string
    events = response.css('div.entry-content p').extract()
    #extracts each line as its own string
            #events_text = response.css('div.entry-content p::text').extract()
    
    #splices out the intro paragraphs on the page
    events = events[2:10]
    
    #FOR TESTING. just grabs one event so I can try and splice out the uneeded characters
    event1 = events[0]
    #splits up an event at its line breaks
    event1_split = event1.split("<br>")

    #NOW: trying to substitute the character patterns below for empty spaces
        #so far, it's not working and it only lets me replace the first thing.
        #I dont want to go thru a for loop for each pattern, so I need to find a more
        #efficient way to make this work. 
    for line in event1_split:
        re.sub('<p>', '', line)
        re.sub('</p>', '', line)
        re.sub('<strong>', '', line)
        re.sub('</strong>', '', line)
        re.sub('\n', '', line)
        #maybe to be used for finding multiple patterns in re.sub (below):
                #'\s+(<p>|</p>|<strong>|</strong>|\n)\s*$'

    for event in events:
        """
        if len(lines) == 4:
            location = lines[1:2]
            address = lines[3]
        if len(lines) == 3:
            location = lines[1]
            address = lines[2]
        """

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the `Open Civic Data
        event standard <http://docs.opencivicdata.org/en/latest/data/event.html>`_.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """
        for item in response.css('.entry-content'):
            yield {
                '_type': 'event',
                'id': self._parse_id(item),
                'name': 'Chicago Public Library Board Meeting Schedule'
                'description': '',
                'classification': 'Board meeting'
                'start_time': ''
                'end_time': '',
                'all_day': self._parse_all_day(item),
                'status': self._parse_status(item),
                'location': self._parse_location(item),
            }

        # self._parse_next(response) yields more responses to parse if necessary.
        # uncomment to find a "next" url
        # yield self._parse_next(response)

    def _parse_next(self, response):
        """
        Get next page. You must add logic to `next_url` and
        return a scrapy request.
        """
        next_url = None  # What is next URL?
        return scrapy.Request(next_url, callback=self.parse)

    def _parse_id(self, item):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        """
        return None

    def _parse_classification(self, item):
        """
        Parse or generate classification (e.g. town hall).
        """
        return 'Not classified'

    def _parse_status(self, item):
        """
        Parse or generate status of meeting. Can be one of:

        * cancelled
        * tentative
        * confirmed
        * passed

        By default, return "tentative"
        """
        return 'tentative'

    def _parse_location(self, item):
        """
        Parse or generate location. Url, latitutde and longitude are all
        optional and may be more trouble than they're worth to collect.
        """
        #how to get the URL of the location? auto-google to grab?

        """
        event = item.xpath('//para/text()[child::br]')
        if len(event) == 3:
            location = event[1]+event[2]
            address = event[3]
        else if len(event) == 2:
            location = event[1]
            address = event
        for line in event:
        address = 
        """

        return {
            'url': None,
            'name': None,
            'coordinates': {
              'latitude': None,
              'longitude': None,
            },
        }

    def _parse_all_day(self, item):
        """
        Parse or generate all-day status. Defaults to false.
        """
        return False

    def _parse_name(self, item):
        """
        Parse or generate event name.
        """
        return None

    def _parse_description(self, item):
        """
        Parse or generate event name.
        """
        return None

    def _parse_start(self, item):
        """
        Parse start date and time.
        """
        s = response.css('strong::text').extract()
        tz = timezone('America/Chicago')


    def _parse_end(self, item):
        """
        Parse end date and time.
        """
        return None
