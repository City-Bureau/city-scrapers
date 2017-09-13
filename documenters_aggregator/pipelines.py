# -*- coding: utf-8 -*-

# Pipelines to store scraped items using SQLAlchemy, AirTable, or a dummy logger.
#
# Set the ITEM_PIPELINES setting in settings.py to use one or more
# of these pipelines.

import os
import requests

from scrapy.exceptions import CloseSpider

AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')


class DocumentersAggregatorLoggingPipeline(object):
    """
    Dummy logging pipeline. Enabled by default, it reminds developers to
    turn on some kind of backend storage pipeline.
    """
    def process_item(self, item, spider):
        spider.logger.warn('Processing {0}. Enable a database pipeline to save items.'.format(item.get('title', 'No title found')))
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
        self.airtable = Airtable('appYfsu9CjuuZt7sF', 'Raw data')

    def process_item(self, item, spider):
        item['id'] = self._make_id(item, spider)
        item['location'] = 'tk'
        item['all_day'] = 'false'
        self.save_item(item, spider)
        return item

    def save_item(self, item, spider):
        airtable_item = self.airtable.match('id', item['id'])
        if airtable_item:
            # update
            spider.logger.debug('AIRTABLE PIPELINE: Updating {0}'.format(item['id']))
            self.airtable.update(airtable_item['id'], item)
        else:
            # create
            spider.logger.debug('AIRTABLE PIPELINE: Creating {0}'.format(item['id']))
            self.airtable.insert(item)

    def _make_id(self, item, spider):
        return '{3} {2} ({0}-{1})'.format(
                                spider.name,
                                item['id'],
                                item['name'],
                                spider.long_name
                            )
