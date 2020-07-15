from .base import *  # noqa

USER_AGENT = "City Scrapers [production mode]. Learn more and say hello at https://cityscrapers.org"  # noqa

# Configure item pipelines
ITEM_PIPELINES = {
    "city_scrapers_core.pipelines.MeetingPipeline": 400,
}

SPIDER_MIDDLEWARES = {
    "city_scrapers.middleware.CityScrapersWaybackMiddleware": 500,
}

EXTENSIONS = {
    "scrapy.extensions.closespider.CloseSpider": None,
}
