class CityScrapersLoggingPipeline(object):
    """
    Dummy logging pipeline. Enabled by default, it reminds developers to
    turn on some kind of backend storage pipeline.
    """
    def process_item(self, item, spider):
        spider.logger.warn('Processing {0}. Enable a database pipeline to save items.'.format(item.get('title', 'No title found')))
        return item
