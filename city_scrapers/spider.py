# -*- coding: utf-8 -*-

from datetime import datetime, date
from pytz import timezone
from inflector import Inflector, English
import scrapy

from city_scrapers.constants import CANCELED, CONFIRMED, PASSED, TENTATIVE


class Spider(scrapy.Spider):
    inflector = Inflector(English)

    def __init__(self, *args, **kwargs):
        # Add parameters for feed storage in Chicago time
        tz = timezone('America/Chicago')
        now = tz.localize(datetime.now())
        self.year = now.year
        self.month = now.strftime('%m')
        self.day = now.strftime('%d')
        self.hour_min = now.strftime('%H%M')
        super().__init__(*args, **kwargs)

    def _generate_id(self, data):
        """
        Calulate ID. ID must be unique within the data source being scraped.
        """
        name = self.inflector.underscore(data['name']).strip('_')
        id = data.get('id', 'x').replace('/', '-')

        # Try to get the start date and time in YYYYmmddHHMM
        # Replace missing start date or times with 0's
        try:
            start_date_str = data['start']['date'].strftime('%Y%m%d')
        except (KeyError, TypeError):
            start_date_str = '00000000'
        try:
            start_time_str = data['start']['time'].strftime('%H%M')
        except (KeyError, TypeError, AttributeError):
            start_time_str = '0000'
        start_str = '{0}{1}'.format(start_date_str, start_time_str)

        parts = [self.name, start_str, id, name]
        return '/'.join(parts)

    def _generate_status(self, data, text):
        """
        Generates one of the following statuses:
        * cancelled: the word 'cancelled' or 'rescheduled' is `text`
        * tentative: event both does not have an agenda and the event is > 7 days away
        * confirmed: either an agenda is posted or the event will happen in <= 7 days
        * passed: event happened in the past
        """
        if ('cancel' in text.lower()) or ('rescheduled' in text.lower()):
            return CANCELED

        try:
            start = data['start']['date']
            # check if event is in the past
            if start < date.today():
                return PASSED
            # check if the event is within 7 days
            elif (start - date.today()).days <= 7:
                return CONFIRMED
        except (KeyError, TypeError):
            pass

        # look for an agenda
        documents = data.get('documents', [])
        for doc in documents:
            if 'agenda' in doc.get('note', '').lower():
                return CONFIRMED

        return TENTATIVE

    def _naive_datetime_to_tz(self, datetime_object, source_tz='America/Chicago'):
        """
        Converts a naive datetime (one without timezone information) by
        interpreting it using the source_tz.
        """
        tz = timezone(source_tz)
        return tz.localize(datetime_object)
