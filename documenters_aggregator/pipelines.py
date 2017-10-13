# -*- coding: utf-8 -*-

# Pipelines to store scraped items using SQLAlchemy, AirTable, or a dummy logger.
#
# Set the ITEM_PIPELINES setting in settings.py to use one or more
# of these pipelines.

import os
import datetime
import dateutil.parser
import json
import time

from airtable import Airtable
from documenters_aggregator.utils import get_key
from random import randint
from requests.exceptions import HTTPError
from scrapy.exceptions import DropItem

AIRTABLE_BASE_KEY = os.environ.get('DOCUMENTERS_AGGREGATOR_AIRTABLE_BASE_KEY')
AIRTABLE_DATA_TABLE = os.environ.get('DOCUMENTERS_AGGREGATOR_AIRTABLE_DATA_TABLE')
FIELDS_WHITELIST = ['id', 'name', 'description', 'classification', 'start_time', 'start_time_formatted', 'end_time', 'end_time_formatte', 'status', 'agency_name', 'location_name', 'location_url', 'location_name', 'location_address', 'location_latitude', 'location_longitude']


class DocumentersAggregatorLoggingPipeline(object):
    """
    Dummy logging pipeline. Enabled by default, it reminds developers to
    turn on some kind of backend storage pipeline.
    """
    def process_item(self, item, spider):
        spider.logger.info('Processing {0} ({1}-{2}). Enable a database pipeline to save items.'.format(item.get('name'), spider.name, item.get('id')))
        return item


class DocumentersAggregatorSQLAlchemyPipeline(object):
    """
    Stub pipeline to save to SQLAlchemy.
    """
    def process_item(self, item, spider):
        return item


class DocumentersAggregatorAirtablePipeline(object):
    """
    Stub pipeline to save to AirTable.
    """
    def __init__(self):
        self.airtable = Airtable(AIRTABLE_BASE_KEY, AIRTABLE_DATA_TABLE)

    def process_item(self, item, spider):
        # copy item; airtable-specific munging is happening here that breaks
        # opencivicdata standard

        if item.get('start_time'):
            dt = dateutil.parser.parse(item['start_time'])
            if dt < datetime.datetime.now(dt.tzinfo):
                return item
        else:
            return item

        time.sleep(randint(0, 3))

        new_item = item.copy()

        # make id
        new_item['id'] = self._make_id(new_item, spider)

        # flatten location
        new_item['location_url'] = get_key(new_item, 'location.url')
        new_item['location_name'] = get_key(new_item, 'location.name')
        new_item['location_address'] = get_key(new_item, 'location.address')
        new_item['location_latitude'] = get_key(new_item, 'location.coordinates.latitude')
        new_item['location_longitude'] = get_key(new_item, 'location.coordinates.longitude')

        new_item['all_day'] = 'false'

        new_item['agency_name'] = spider.long_name

        new_item['start_time_formatted'] = self._transform_date(new_item['start_time'])
        new_item['end_time_formatted'] = self._transform_date(new_item['end_time'])

        new_item = { k:v for k,v in new_item.items() if k in FIELDS_WHITELIST }

        try:
            self.save_item(new_item, spider)
            return item
        except HTTPError as e:
            spider.logger.error('HTTP error')
            spider.logger.error(e.response.content)
            spider.logger.exception('Original message')
            spider.logger.error(json.dumps(new_item, indent=4, sort_keys=True))
            raise DropItem('Could not save {0}'.format(new_item['id']))
        except Exception as e:
            spider.logger.exception('Unknown error')

    def save_item(self, item, spider):
        now = datetime.datetime.now().isoformat()
        airtable_item = self.airtable.match('id', item['id'])
        if airtable_item:
            # update
            spider.logger.debug('AIRTABLE PIPELINE: Updating {0}'.format(item['id']))
            item['scrape_date_updated'] = now
            self.airtable.update(airtable_item['id'], item)
        else:
            # create
            spider.logger.debug('AIRTABLE PIPELINE: Creating {0}'.format(item['id']))
            item['scrape_date_updated'] = now
            item['scrape_date_initial'] = now
            self.airtable.insert(item)

    def _make_id(self, item, spider):
        return '{spider_long_name} {item_name} ({spider_name}-{item_id})'.format(spider_name=spider.name, spider_long_name=spider.long_name, item_id=item['id'], item_name=item['name'])

    def _transform_date(self, timestring):
        """
        Parse to friendly format for Zapier integration.
        """
        try:
            dt = dateutil.parser.parse(timestring)
        except TypeError:
            return None

        return dt.strftime('%a %B %d, %Y, %I:%M%p')
