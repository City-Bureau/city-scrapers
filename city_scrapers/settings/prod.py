from .base import *

USER_AGENT = 'City Scrapers [production mode]. Learn more and say hello at https://citybureau.org/city-scrapers'

# Configure item pipelines
ITEM_PIPELINES = {
    "city_scrapers.pipelines.MigrationPipeline": 200,
    "city_scrapers_core.pipelines.MeetingPipeline": 300,
    "city_scrapers_core.pipelines.JSCalendarPipeline": 400,
}

SPIDER_MIDDLEWARES = {
    "city_scrapers_core.middlewares.AzureDiffMiddleware": 543,
}

EXTENSIONS = {
    "scrapy_sentry.extensions.Errors": 10,
    "city_scrapers_core.extensions.AzureBlobStatusExtension": 100,
    "scrapy.extensions.closespider.CloseSpider": None,
}

FEED_EXPORTERS = {
    'json': 'scrapy.exporters.JsonItemExporter',
    'jsonlines': 'scrapy.exporters.JsonLinesItemExporter',
}

FEED_FORMAT = 'jsonlines'

FEED_STORAGES = {
    'azure': 'city_scrapers_core.extensions.azure_storage.AzureBlobFeedStorage',
}

AZURE_ACCOUNT_NAME = os.getenv('AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = os.getenv('AZURE_ACCOUNT_KEY')
AZURE_CONTAINER = os.getenv('AZURE_CONTAINER')

CITY_SCRAPERS_STATUS_CONTAINER = os.getenv('AZURE_STATUS_CONTAINER')

FEED_URI = (
    'azure://{account_name}:{account_key}@{container}'
    '/%(year)s/%(month)s/%(day)s/%(hour_min)s/%(name)s.json'
).format(
    account_name=AZURE_ACCOUNT_NAME,
    account_key=AZURE_ACCOUNT_KEY,
    container=AZURE_CONTAINER,
)

FEED_PREFIX = "%Y/%m/%d"
