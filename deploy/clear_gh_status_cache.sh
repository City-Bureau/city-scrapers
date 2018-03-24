#! /bin/bash

curl -sS https://github.com/City-Bureau/city-scrapers | pup 'table img[src*="camo"] attr{src}' | xargs curl -X PURGE
