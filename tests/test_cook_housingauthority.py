# import pytest

# from city_scrapers.spiders.cook_housingauthority import CookHousingAuthoritySpider
# from tests.utils import file_response


# # def test_gen_requests():
# #     spider = CookHousingAuthoritySpider()
# #     test_response = file_response('files/hacc_feed.txt', 'http://thehacc.org/events/feed/')
# #     requests = list(spider._gen_requests(test_response))
# #     assert requests == [
# #         'http://thehacc.org/wp-json/tribe/events/v1/events/2836',
# #         'http://thehacc.org/wp-json/tribe/events/v1/events/2816',
# #         'http://thehacc.org/wp-json/tribe/events/v1/events/2650',
# #         'http://thehacc.org/wp-json/tribe/events/v1/events/2882',
# #         'http://thehacc.org/wp-json/tribe/events/v1/events/2858',
# #         'http://thehacc.org/wp-json/tribe/events/v1/events/2879',
# #     ]


# # @pytest.fixture(scope='module')
# # def item():
# #     spider = CookHousingAuthoritySpider()
# #     test_response = file_response('files/hacc_event.json', 'http://thehacc.org/wp-json/tribe/events/v1/events/2644')
# #     yield from spider._parse_event(test_response)

# ##### Values designed to vary #####

# # def test_id(item):
# #    assert item['id'] == 'cook_housingauthority/201805111000/x/entrepreneurship_boot_camp_session_2_marketing_plan'

# def test_name(item):
#     assert item['name'] == 'Entrepreneurship Boot Camp Session 2, Marketing Plan'

# def test_description(item):
#     assert item['description'] == 'Learn how to start and run your own business. See the attached flyer for more details about workshops. FSS participants, Entrepreneurship Boot camp will help you reach your “open my own business” goal. Register today!'

# def test_start_time(item):
#     assert item['start_time'].isoformat() == '2018-05-11T10:00:00-05:00'

# def test_end_time(item):
#     assert item['end_time'].isoformat() == '2018-05-11T12:00:00-05:00'

# def test_location(item):
#     assert item['location']== {'address': '15306 S. Robey Ave., Harvey Il 60426',
#     'coordinates': {'latitude': None, 'longitude': None},
#     'name': 'Turlington West Community Room',
#     'url': None}

# def test_sources(item):
#     assert item['sources'] == [{'note': '',
#     'url': 'http://thehacc.org/event/entrepreneurship-boot-camp-session-2-marketing-analysis/'}]


# ##### Static values #####

# def test_type(item):
#     assert item['_type'] == 'event'

# def test_allday(item):
#     assert item['all_day'] is False

# def test_classification(item):
#     assert item['classification'] == 'Not classified'

# def test_status(item):
#     assert item['status'] == 'tentative'

# def test_timezone(item):
#     assert item['timezone'] == 'America/Chicago'
