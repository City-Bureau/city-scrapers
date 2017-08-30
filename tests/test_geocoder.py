# -*- coding: utf-8 -*-

import betamax
import requests

from tests.utils import test_item
from documenters_aggregator.pipelines.geocoder import GeocoderPipeline


def test_geocoding():
    item = test_item()
    item['location']['coordinates'] = None

    with requests.Session() as session:
        recorder = betamax.Betamax(session)

    with recorder.use_cassette('test_geocoding'):
        geocoder = GeocoderPipeline(session)
        geocoder.process_item(item, None)

    expected = {'latitude': '41.8838677', 'longitude': '-87.6319365'}
    assert item['location']['coordinates'] == expected
