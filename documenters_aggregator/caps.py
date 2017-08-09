# -*- coding: utf-8 -*-
import requests, json

LOOKUP_URL = "https://home.chicagopolice.org/wp-content/themes/cpd-bootstrap/proxy/miniProxy.php?https://home.chicagopolice.org/get-involved-with-caps/all-community-event-calendars/"

headers = {
'User-Agent': 'Mozilla/5.0 (Linux; <Android Version>; <Build Tag etc.>) AppleWebKit/<WebKit Rev> (KHTML, like Gecko) Chrome/<Chrome Rev> Mobile Safari/<WebKit Rev>'
}

r = requests.get(LOOKUP_URL, headers=headers)
response = r.json()

print(response)
