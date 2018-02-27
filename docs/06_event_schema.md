# Event schema

Our data model for events is based on the [Event Object](http://docs.opencivicdata.org/en/latest/data/event.html) from the [Open Civic Data](http://docs.opencivicdata.org) project.

For our initial scrapers, we are focusing on basic event data. Over time, this
may expand to include meeting notes, agendas, etc.

Empty strings are preferred to Nones.

```python
{
  '_type': 'event',                              # required value
  'id': 'unique identifier'                      # required string in format:
                                                 # <spider-name>/<start-time-in-YYYYMMddhhmm>/<unique-id>/<underscored-event-name>
  'name': 'Committee on Pedestrian Safety',      # required string
  'description': 'A longer description',         # optional string
  'classification': 'Public Safety'              # general topic of the meeting
  'start_time': datetime(2018, 1, 10, 11, ...),  # required datetime object
                                                 # '17:30:00-06:00' means 5:30PM Chicago (UTC-6) time
  'end_time': None,                              # optional datetime object
  'timezone': 'America/Chicago',                 # required timezone in tzinfo format
  'all_day': False,                              # must be True or False

  'location': {                                  # required dictionary
    'url': '',                                   # empty string; will be filled in by geocoder
    'name': 'City Hall, Room 201A',              # optional name of the location
    'address': '121 N LaSalle Dr, Chicago, IL',  # required address of the location
    'coordinates': {                             # must be: None or dictionary
      'latitude': '',                            # empty string; will be filled in by geocoder
      'longitude': ''                            # empty string; will be filled in by geocoder
    }
  },

  'sources': [                                   # required list of sources
    {
      'url': '',                                 # required URL where data was scraped from
      'note': ''                                 # optional info about how the data was scraped
    }
  ]
}
```
