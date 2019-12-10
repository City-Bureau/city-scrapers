from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import ChiRogersParkSsaMixin


class ChiSsa43Spider(ChiRogersParkSsaMixin, CityScrapersSpider):
    name = "chi_ssa_43"
    agency = "Chicago Special Service Area #43 Devon Avenue"
    start_urls = ["https://rpba.org/ssa-43/"]
