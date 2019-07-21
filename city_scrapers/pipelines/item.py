from city_scrapers.utils import report_error


class CityScrapersItemPipeline(object):
    """
    Pipeline for doing any custom processing on individual items
    """
    @report_error
    def process_item(self, item, spider):
        item['agency'] = spider.agency
        return item
