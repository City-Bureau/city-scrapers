from city_scrapers.utils import report_error

@report_error
class CityScrapersItemPipeline(object):
    """
    Pipeline for doing any custom processing on individual
    items, i.e. assigning the long name to agency_name
    """
    def process_item(self, item, spider):
        raise Exception("HELLO")
        
        if hasattr(spider, 'long_name'):
            item['agency_name'] = spider.long_name
        else:
            item['agency_name'] = spider.agency_id
        return item
