from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import ChiRogersParkSsaMixin


class ChiSsa19Spider(ChiRogersParkSsaMixin, CityScrapersSpider):
    name = "chi_ssa_19"
    agency = "Chicago Special Service Area #19 Howard Street"
    start_urls = ["https://rpba.org/ssa-19/"]
