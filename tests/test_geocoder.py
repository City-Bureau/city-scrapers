# -*- coding: utf-8 -*-

import pytest

from tests.utils import test_item
from documenters_aggregator.pipelines.geocoder import GeocoderPipeline

def test_geocoding():
    item = test_item()

    geocoder = GeocoderPipeline()
    geocoded = geocoder.process_item(item, None)

    expected = { 'latitude': '41.883868', 'longitude': '-87.631936' }
    assert item['location']['coordinates'] == expected

