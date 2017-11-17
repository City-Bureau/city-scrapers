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
FIELDS_WHITELIST = ['id', 'name', 'description', 'classification', 'start_time', 'end_time', 'timezone', 'status', 'agency_name', 'location_name', 'location_url', 'location_name', 'location_address', 'location_latitude', 'location_longitude', 'geocode', 'url', 'scrape_date_initial', 'scrape_date_update']


class AirtablePipeline(object):
    """
    Stub pipeline to save to AirTable.
    """
    def __init__(self):
        self.airtable = Airtable(AIRTABLE_BASE_KEY, AIRTABLE_DATA_TABLE)

    def process_item(self, item, spider):
        # copy item; airtable-specific munging is happening here that breaks
        # opencivicdata standard

        if item.get('start_time') is None:
            spider.logger.debug('AIRTABLE PIPELINE: Ignoring event without start_time {0}'.format(item['id']))
            return item

        dt = dateutil.parser.parse(item['start_time'])
        if dt < datetime.datetime.now(dt.tzinfo):
            spider.logger.debug('AIRTABLE PIPELINE: Ignoring past event {0}'.format(item['id']))
            return item

        time.sleep(randint(0, 3))  # to avoid rate limiting?

        new_item = item.copy()

        # flatten location
        new_item['location_url'] = get_key(new_item, 'location.url')
        new_item['location_name'] = get_key(new_item, 'location.name')
        new_item['location_address'] = get_key(new_item, 'location.address')
        new_item['location_latitude'] = get_key(new_item, 'location.coordinates.latitude')
        new_item['location_longitude'] = get_key(new_item, 'location.coordinates.longitude')
        new_item['timezone'] = 'America/Chicago'  # TODO have this passed in by the spiders
        new_item['all_day'] = 'false'
        new_item['agency_name'] = spider.long_name

        new_item = {k: v for k, v in new_item.items() if k in FIELDS_WHITELIST}

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
            spider.logger.debug('AIRTABLE PIPELINE: Updating {0}'.format(item['id']))
            item['scrape_date_updated'] = now
            self.airtable.update_by_field('id', airtable_item['id'], item)
        else:
            spider.logger.debug('AIRTABLE PIPELINE: Creating {0}'.format(item['id']))
            item['scrape_date_updated'] = now
            item['scrape_date_initial'] = now
            self.airtable.insert(item)
