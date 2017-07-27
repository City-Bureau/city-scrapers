# -*- coding: utf-8 -*-

# Pipelines to store scraped items using SQLAlchemy, AirTable, or a dummy logger.
#
# Set the ITEM_PIPELINES setting in settings.py to use one or more
# of these pipelines.


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
    def process_item(self, item, spider):
        return item
