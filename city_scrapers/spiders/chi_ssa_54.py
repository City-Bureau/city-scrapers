from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import ChiRogersParkSsaMixin


class ChiSsa54Spider(ChiRogersParkSsaMixin, CityScrapersSpider):
    name = "chi_ssa_54"
    agency = "Chicago Special Service Area #54 Sheridan Road"
    start_urls = ["https://rpba.org/ssa-54/"]
