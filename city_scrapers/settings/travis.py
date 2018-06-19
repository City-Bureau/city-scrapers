from .base import *

# Configure item pipelines
#
# One of:
# * city_scrapers.pipelines.ValidationPipeline,
# * city_scrapers.pipelines.AirtablePipeline
#
# Or define your own.
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'city_scrapers.pipelines.TravisValidationPipeline': 300,
}

