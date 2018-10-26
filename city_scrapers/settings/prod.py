from .base import *

USER_AGENT = 'City Scrapers [production mode]. Learn more and say hello at https://citybureau.org/city-scrapers'

# Configure item pipelines
#
# One of:
# * city_scrapers.pipelines.CityScrapersLoggingPipeline,
# * city_scrapers.pipelines.AirtablePipeline
#
# Or define your own.
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'city_scrapers.pipelines.CityScrapersItemPipeline': 200,
    'city_scrapers.pipelines.s3_item.CityScrapersS3ItemPipeline': 300,
    'city_scrapers.pipelines.AirtablePipeline': 400
}

EXTENSIONS = {
    "scrapy_sentry.extensions.Errors": 10,
    'scrapy.extensions.closespider.CloseSpider': None,
}


FEED_EXPORTERS = {
    'cityscrapers_jsonlines':
        'city_scrapers.exporters.CityScrapersJsonLinesItemExporter'
}

FEED_STORAGES = {
    'azure': 'city_scrapers.extensions.feedexport.AzureBlobFeedStorage',
}

FEED_FORMAT = 'cityscrapers_jsonlines'

FEED_URI = (
    'azure://{account_name}:{account_key}@{container}'
    '/%(year)s/%(month)s/%(day)s/%(hour_min)s/%(name)s.json'
).format(
    account_name=AZURE_ACCOUNT_NAME,
    account_key=AZURE_ACCOUNT_KEY,
    container=AZURE_CONTAINER,
)
