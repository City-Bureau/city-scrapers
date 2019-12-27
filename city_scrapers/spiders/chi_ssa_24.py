from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import ChiRogersParkSsaMixin


class ChiSsa24Spider(ChiRogersParkSsaMixin, CityScrapersSpider):
    name = "chi_ssa_24"
    agency = "Chicago Special Service Area #24 Clark/Morse/Glenwood"
    start_urls = ["https://rpba.org/ssa-24/"]
