from city_scrapers.utils import report_error


class CityScrapersItemPipeline(object):
    """
    Pipeline for doing any custom processing on individual
    items
    """
    @report_error
    def process_item(self, item, spider):
        item['agency_name'] = spider.agency_name
        # Remove cancellation from names, update ID if changed
        cleaned_name = spider._clean_name(item['name'])
        if cleaned_name != item['name']:
            item['name'] = cleaned_name
            item['id'] = spider._generate_id(item)
        return item
