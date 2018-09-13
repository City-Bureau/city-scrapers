# Event schema

Our data model for events is based on the [Event Object](http://docs.opencivicdata.org/en/latest/data/event.html) from the [Open Civic Data](http://docs.opencivicdata.org) project.

"Required" means that the value cannot be `None`, an empty string, empty dictionary nor empty list. "Optional" means that `None` or empty values are ok.

```python
{
  '_type': 'event',                              # required value
  
  'id': 'unique identifier'                      # required string in format:
                                                 # <spider-name>/<start-time-in-YYYYMMddhhmm>/<unique-id>/<underscored-event-name>
                                                 # if start-time is missing, replace hhmm with 0000
                                                 
  'name': 'Committee on Pedestrian Safety',      # required string, name of the event
  
  'event_description': 'A longer description',   # optional string, event description
  
  'all_day': False,                              # required boolean, whether or not the event lasts all day
  
  'status': 'tentative',                         # required string, one of the following:
                                                 # 'cancelled': event is listed as cancelled or rescheduled
                                                 # 'tentative': event both does not have an agenda and the event is > 7 days away
                                                 # 'confirmed': either an agenda is posted or the event will happen in <= 7 days
                                                 # 'passed': event happened in the past
  
  'classification': 'board meeting',             # optional string. This field is used by some spiders
                                                 # to differentiate between board and various committee
                                                 # meetings. Ask @diaholliday if unsure.

  'start': {                                     # required dictionary
    'date': date(2018, 12, 31),                  # required datetime.date object in local timezone
    'time': None,                                # optional datetime.time object in local timezone
    'note': 'in the afternoon'                   # optional string, supplementary information if there’s no start time
  },
   
  'end': {                                       # required dictionary
    'date': date(2018, 12, 31),                  # optional datetime.date object in local timezone
    'time': time(13, 30),                        # optional datetime.time object in local timezone
    'note': 'estimated 2 hours after start time' # optional string, supplementary information if there’s no end time
  },   

  'location': {                                  # required dict of event locations
                                                 # for multiple locations: make a different event with unique id for each location
    'address': '121 N LaSalle Dr, Chicago, IL',  # required string, address of the location
    'name': 'City Hall, Room 201A',              # optional string, name of the location
    'neighborhood': 'Loop'                       # optional string, use community area in Chicago
  },
  
  'documents': [                                 # optional list of documents
    {
      'url': 'http://www.example.com/agenda.pdf',# required string, URL to the document
      'note': 'agenda'                           # required string, name of the document
    }
  ],

  'sources': [                                   # required list of sources
    {
      'url': '',                                 # required string, URL where data was scraped from
      'note': ''                                 # optional string, info about how the data was scraped
    }
  ]
}
```

# Spider attributes
In addition, each spider records the following data as attributes:
```python
class ChiAnimalSpider(Spider):
    name = 'chi_animal'                              # name of spider in lowercase
    agency_name = 'Animal Care and Control Commission' # name of agency
    timezone = 'America/Chicago'                     # timezone of the events in tzinfo format
```
