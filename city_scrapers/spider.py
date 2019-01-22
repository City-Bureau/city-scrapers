# -*- coding: utf-8 -*-

import re
from datetime import date

from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.constants import CANCELED, CONFIRMED, PASSED, TENTATIVE


class Spider(CityScrapersSpider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'agency_name'):
            self.agency = self.agency_name

    def _clean_name(self, name):
        """Remove canceled strings from name"""
        return re.sub(
            r'([\s:-]{1,3})?(cancel\w+|rescheduled)([\s:-]{1,3})?', '', name, flags=re.IGNORECASE
        )

    def _generate_id(self, data):
        underscore_title = re.sub(
            r"\s+", "_",
            re.sub(r"[^A-Z^a-z^0-9^]+", " ", data["name"]).strip()
        ).lower()
        item_id = data.get("id", "x").replace("/", "-")
        try:
            start_date_str = data['start']['date'].strftime('%Y%m%d')
        except (KeyError, TypeError):
            start_date_str = '00000000'
        try:
            start_time_str = data['start']['time'].strftime('%H%M')
        except (KeyError, TypeError, AttributeError):
            start_time_str = '0000'
        start_str = '{}{}'.format(start_date_str, start_time_str)
        return '/'.join([self.name, start_str, item_id, underscore_title])

    def _generate_status(self, data, text=''):
        """
        Generates one of the allowed statuses from constants based on
        the name and time of the meeting
        """
        # Combine all relevant meeting text to find words relating to meeting status changes
        meeting_text = ' '.join([
            data.get('name', ''),
            data.get('event_description', ''),
            text,
        ]).lower()
        if any(word in meeting_text for word in ['cancel', 'rescheduled', 'postpone']):
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
