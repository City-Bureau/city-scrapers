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
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': 'Bearer {0}'.format(AIRTABLE_API_KEY),
            'Content-type': 'application/json',
        })

    def process_item(self, item, spider):
        # import ipdb; ipdb.set_trace();
        item['id'] = self._make_id(item, spider)
        item['location'] = 'how to encode?'
        item['all_day'] = 'false'

        self.save_item(item, spider)
        # raise CloseSpider('testing')
        return item

    def save_item(self, item, spider):

        # https://api.airtable.com/v0/appYfsu9CjuuZt7sF/Raw%20data?maxRecords=3&view=Grid%20view

        url = 'https://api.airtable.com/v0/appYfsu9CjuuZt7sF/Raw data'
        params = {
            'view': 'Grid view',
            'filterByFormula': "{{id}} = '{0}'".format(item['id']),
        }

        resp = self.session.get(url, params=params)
        records = resp.json().get('records', [])

        if len(records) == 1:
            # update
            item['name'] = 'bored of directors'
            update_url = '{0}/{1}'.format(url, records[0]['id'])
            save_resp = self.session.patch(update_url, json={'fields': item})
            # import ipdb; ipdb.set_trace();
            pass
        elif len(records) > 1:
            # data validation error
            pass
        else:
            # create
            save_resp = self.session.post(url, json={'fields': item})
            pass

        pass

    def _make_id(self, item, spider):
        return '{0}-{1}'.format(
                                spider.name,
                                item['id'],
                            )
