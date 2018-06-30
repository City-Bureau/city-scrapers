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
    # disabled until we can rebuild it on another provider
    #'city_scrapers.pipelines.GeocoderPipeline': 200,
    'city_scrapers.pipelines.CityScrapersItemPipeline': 200,
    'city_scrapers.pipelines.CityScrapersS3ItemPipeline': 300,
    'city_scrapers.pipelines.AirtablePipeline': 400
}

EXTENSIONS = {
    "scrapy_sentry.extensions.Errors": 10,
    'scrapy.extensions.closespider.CloseSpider': None,
}


FEED_EXPORTERS = {
    'cityscrapers_jsonlines': 'city_scrapers.exporters.CityScrapersJsonLinesItemExporter'
}

FEED_FORMAT = 'cityscrapers_jsonlines'
FEED_URI = 's3://city-scrapers-events-feed/%(name)s/%(year)s/%(month)s/%(day)s/%(hour_min)s.json'
