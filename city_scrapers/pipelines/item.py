from city_scrapers.utils import report_error


class CityScrapersItemPipeline(object):
    """
    Pipeline for doing any custom processing on individual
    items, i.e. assigning the long name to agency_name
    """
    @report_error
    def process_item(self, item, spider):
        if hasattr(spider, 'long_name'):
            item['agency_name'] = spider.long_name
        else:
            item['agency_name'] = spider.agency_name
        return item
