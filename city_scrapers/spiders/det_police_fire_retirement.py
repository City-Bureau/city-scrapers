from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import DetRetirementMixin


class DetPoliceFireRetirementSpider(DetRetirementMixin, CityScrapersSpider):
    name = 'det_police_fire_retirement'
    agency = 'Detroit Police and Fire Retirement System'
    start_urls = [
        'http://www.rscd.org/member_resources/board_of_trustees/past_meeting_agendas___minutes.php',
        'http://www.rscd.org/member_resources/investment_committee/past_meeting_agendas___minutes.php',  # noqa
    ]
