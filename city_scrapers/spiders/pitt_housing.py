# -*- coding: utf-8 -*-
import scrapy
from datetime import date
from html.parser import HTMLParser

from dateutil.parser import parse as dtparse

from city_scrapers.spider import Spider
from city_scrapers.constants import *



class PittHousingSpider(Spider):
    name = 'pitt_housing'
    agency_name = 'Housing Authority of the City of Pittsburgh'
    timezone = 'America/New_York'
    allowed_domains = ['www.hacp.org']
    start_urls = ['http://www.hacp.org/public-information/board-info']

    def parse(self, response):
        """
        `parse` should always `yield` a dict that follows the Event Schema
        <https://city-bureau.github.io/city-scrapers/06_event_schema.html>.

        Change the `_parse_id`, `_parse_name`, etc methods to fit your scraping
        needs.
        """

        for item in self._create_meetings(response): 

            data = {
                '_type': 'event',
                'name': 'Board of Commissioners',
                'event_description': '',
                'classification': BOARD,
                'start': self._parse_start(item),
                'end': {'date': None, 'time': None, 'note': None},
                'all_day': False,
                'location': {
                    'address': 'Civic Building, 200 Ross St., Pittsburgh, PA, 15219',
                    'name': '',
                    'neighborhood': ''
                },
                'documents': self._parse_documents(item),
                'sources': [{
                    'url': self.start_urls[0],
                    'note': ''}]
            }

            data['status'] = self._generate_status(data)
            data['id'] = self._generate_id(data)

            yield data

    def _create_meetings(self, response):
        """
        Returns a list containing lists corresponding to each meeting.
        """
        meetings = []
        parser = MyHTMLParser()
        meetings_xpath = '//div[@id="the-copy"]/div[2]/p[contains(strong, "2018 HACP Board Agendas")]/following-sibling::p'

        for item in response.xpath(meetings_xpath).extract():  
            parser.feed(item)
            meeting = [parser.date, [parser.doc_url]]

            # If meetings is empty, append meeting
            if not meetings:
                meetings.append(meeting)

            # If meetings is not empty, get the last meeting date and compare 
            # it to parser.date. Append parser.doc_url to last meeting if 
            # parser.date == the last meeting date. Otherwise, append the whole
            # meeting to meetings.
            else:
                last_meeting = meetings[-1]
                last_meeting_date = last_meeting[0]                
                if parser.date == last_meeting_date:
                    if parser.doc_url:
                        last_meeting[1].append(parser.doc_url)  
                else: 
                    meetings.append(meeting)

        return meetings

    def _parse_start(self, item):
        """
        Parse start date and time.
        """

        date_string = item[0]
        try:
            dt = dtparse(date_string)
            return {'date': dt.date(), 'time': None, 'note': None}
        except ValueError:
            return {'date': None, 'time': None, 'note': None}

    def _parse_documents(self, item):
        """
        Parse or generate documents.
        """

        # Create documents, which will be a list of dictionaries corresponding 
        # to each agenda or minutes document found.
        documents = []
        for doc in item[1]: 
            if 'agenda' in doc.lower():
                agenda = {'url': doc, 'note': 'agenda'}
                documents.append(agenda)
            elif 'minutes' in doc.lower():
                minutes = {'url': doc, 'note': 'minutes'}
                documents.append(minutes)

        return documents

class MyHTMLParser(HTMLParser):
    """"
    Creates object that inherits from HTMLParser. Used to parse individual 
    lines of HTML for dates and document URLs.
    Attributes:
        doc_url: A string containing a document URL found in HTML
        date: A string containing the date found in HTML.
    """

    doc_url = ''
    date = ''

    def handle_starttag(self, tag, attrs):
        if attrs:
            for attr in attrs:
                for item in attr:
                    if 'http' in item:
                        self.doc_url = item
        else: 
            self.doc_url = ''

    def handle_data(self, data):
        slice_index = data.index('-')
        self.date = data[:slice_index].rstrip()

