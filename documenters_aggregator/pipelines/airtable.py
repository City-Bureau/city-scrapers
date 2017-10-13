class DocumentersAggregatorAirtablePipeline(object):
    """
    Stub pipeline to save to AirTable.
    """
    def __init__(self):
        self.airtable = Airtable(AIRTABLE_BASE_KEY, AIRTABLE_DATA_TABLE)

    def process_item(self, item, spider):
        # copy item; airtable-specific munging is happening here that breaks
        # opencivicdata standard
        new_item = item.copy()

        # make id
        new_item['id'] = self._make_id(new_item, spider)

        # flatten location
        new_item['location_url'] = get_key(new_item, 'location.url')
        new_item['location_name'] = get_key(new_item, 'location.name')
        new_item['location_address'] = get_key(new_item, 'location.address')
        new_item['location_latitude'] = get_key(new_item, 'location.coordinates.latitude')
        new_item['location_longitude'] = get_key(new_item, 'location.coordinates.longitude')

        new_item['all_day'] = 'false'

        del(new_item['location'])
        del(new_item['_type'])

        self.save_item(new_item, spider)

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
        return '{item_name} ({spider_long_name}, {spider_name}-{item_id})'.format(spider_name=spider.name, spider_long_name=spider.long_name, item_id=item['id'], item_name=item['name'])
