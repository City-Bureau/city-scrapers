from .base import *

# Configure item pipelines
ITEM_PIPELINES = {
    'city_scrapers.pipelines.TravisValidationPipeline': 300,
}
