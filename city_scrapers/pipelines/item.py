class CityScrapersItemPipeline(object):
    """
    Pipeline for doing any custom processing on individual
    items, i.e. assigning the long name to agency_name
    """
    def process_item(self, item, spider):
        item['agency_name'] = spider.long_name
        return item
