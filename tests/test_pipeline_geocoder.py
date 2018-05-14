import betamax
import requests
import tests.conftest as config
from tests.utils import test_item
from city_scrapers.pipelines.geocoder import GeocoderPipeline

betamax_config = config.config


def test_geocoding():
    item = test_item()
    item['location']['coordinates'] = None

    session = requests.Session()
    recorder = betamax.Betamax(session, betamax_config.cassette_library_dir)

    with recorder.use_cassette('test_geocoding'):
        geocoder = GeocoderPipeline(session)
        geocoder.geocode_database = {}
        geocoder.process_item(item, None)

    expected = {'latitude': '41.8833466352224', 'longitude': '-87.6323211702195'}
    assert item['location']['coordinates'] == expected
