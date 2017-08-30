# -*- coding: utf-8 -*-

import pytest
import betamax
import requests

from tests.utils import test_item
from documenters_aggregator.pipelines.geocoder import GeocoderPipeline

def test_geocoding():
    item = test_item()

    with requests.Session() as session:
        recorder = betamax.Betamax(session)

    with recorder.use_cassette('test_geocoding'):
        geocoder = GeocoderPipeline(session)
        geocoded = geocoder.process_item(item, None)

    expected = { 'latitude': '41.883868', 'longitude': '-87.631936' }
    assert item['location']['coordinates'] == expected

