from city_scrapers_core.spiders import CityScrapersSpider

from city_scrapers.mixins import DetRetirementMixin


class DetGeneralRetirementSystemSpider(DetRetirementMixin, CityScrapersSpider):
    name = 'det_general_retirement_system'
    agency = 'Detroit General Retirement System'
    start_urls = [
        'http://www.rscd.org/member_resources_/board_of_trustees/past_meeting_agendas___minutes.php',  # noqa
        'http://www.rscd.org/member_resources_/investment_committee/past_meeting_agendas_minutes.php',  # noqa
    ]
