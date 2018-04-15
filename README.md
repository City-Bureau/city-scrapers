[![Build Status](https://travis-ci.org/City-Bureau/city-scrapers.svg?branch=master)](https://travis-ci.org/City-Bureau/city-scrapers)

[![Deploy Status](https://codebuild.us-east-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiZUwxa3FleE42andOVVZhUytOSXFQOE5QMnYwN3Jxa2FmWTBoMk5XZmJTb05OSmtIcXc4SW5ycjZua2x0Zy9SQzN2Q3ZTVW1xRWFrTGRUSVhna2Y3NWtnPSIsIml2UGFyYW1ldGVyU3BlYyI6IklRdldCcXJKMm4zTmFtZXEiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=master)](https://console.aws.amazon.com/codebuild/home?region=us-east-1#/projects/DocumentersAggregator/view)

## Who are the City Bureau Documenters, and why do they want to scrape websites?

Public meetings are important spaces for democracy where any resident can participate and hold public figures accountable. [City Bureau's Documenters program](https://www.citybureau.org/documenters) pays community members an hourly wage to inform and engage their communities by attending and documenting public meetings.

How does the Documenters program know when meetings are happening? It isn’t easy! These events are spread across dozens of websites, rarely in useful data formats.

That’s why City Bureau and ProPublica Illinois are working together with a team of civic coders to develop and coordinate the City Scrapers, a community open source project to scrape and store these meetings in a central database.

## What are the City Scrapers?

The City Scrapers collect information about public meetings. Everyday, the City Scrapers go out and fetch information about new meetings from Chicago city council's website, the local school council's website, the Chicago police department's website, and many more. This happens automatically so that a person doesn't have to do it. The scrapers store all of the meeting information in a database for journalists at City Bureau to report on them. 

Community members are also welcome to use this code to set up their own databases.

## What can I learn from working on the City Scrapers?

A lot about the City of Chicago! What is City Council talking about this week? What are the local school councils, and what community power do they have? What neighborhoods is the police department doing outreach in? Who governs our water?

From building a scraper, you'll gain experience with:  
- how the web works (HTTP requests and responses, reading HTML)  
- writing functions and tests in Python
- version control and collaborative coding (git and Github)
- a basic data file format (json), working with a schema and data validation
- problem solving, finding patterns, designing robust code

## Community Mission

The City Bureau Labs community welcomes contributions from everyone. We prioritize learning and leadership opportunities for under-represented individuals in tech and journalism.
 
We hope that working with us will fill experience gaps (like using git/github, working with data, or having your ideas taken seriously), so that more under-represented people will become decision-makers in both our community and Chicago’s tech and media scenes at large.

## Ready to code with us?

1. [Fill out this form](https://airtable.com/shrsdRcYVzp019U22) to join our [slack channel](https://citybureau.slack.com/#labs_city_scrapers) and meet the community.
2. Read about [how we collaborate](https://github.com/City-Bureau/city-scrapers/blob/master/CONTRIBUTING.md) and review our [Code of Conduct](https://github.com/City-Bureau/city-scrapers/blob/master/CODE_OF_CONDUCT.md).
3. Get started with [Installation](docs/02_installation.md) and [Contributing a spider](docs/03_contribute.md).

We ask all new contributors to start by writing a spider and its documentation or fixing a bug in an existing one in order to gain familiarity with our code and culture. Reach out on [slack](https://citybureau.slack.com/#labs_city_scrapers) for support if you need it. We also meet up in person to work together regularly, and post about upcoming meetups in slack.

For those familiar with the project, please see the [help-wanted Github issues](https://github.com/City-Bureau/city-scrapers/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22).

## Don't want to code?

[Join our slack channel](https://airtable.com/shrsdRcYVzp019U22) (chatroom) to discuss ideas and meet the community!

A. We have ongoing conversations about what sort of data we should collect and how it should be collected. Help us make these decisions by commenting on [issues with a non-coding label](https://github.com/City-Bureau/city-scrapers/issues?q=is%3Aissue+is%3Aopen+label%3Anon-coding).

B. Research sources for public meetings. Answer questions like: Are we scraping events from the right websites? Are there local agencies that we're missing? Should events be updated manually or by a scraper? [Triage events sources on these issues](https://github.com/City-Bureau/city-scrapers/issues?q=is%3Aissue+is%3Aopen+label%3A%22non-coding%3A+triage+events+source%22).

## Scraper Status

### Chicago

| Status / Last Ran | Scraper |
|---------|--------|
| ![Status](https://s3.amazonaws.com/city-scrapers-status/ward_night.svg) | Aldermanic Ward Nights |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/chi_animal.svg) | Animal Care and Control Commission |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/chi_buildings.svg) | Building Commission of Chicago |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/chi_city_college.svg) | City College of Chicago |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/chi_citycouncil.svg) | City Council |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/chi_pubhealth.svg) | Department of Public Health |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/chi_infra.svg) | Infrastructure Trust |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/chi_parks.svg) | Parks District |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/chi_police.svg) | Police Department |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/chi_policeboard.svg) | Police Board |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/chi_library.svg) | Public Library |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/chi_school_actions.svg) | Public Schools: School Actions |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/chi_schools.svg) | Public Schools Board of Education |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/chi_transit.svg) | Transit Authority |

### Cook County

| Status / Last Ran | Scraper |
|---------|--------|
| ![Status](https://s3.amazonaws.com/city-scrapers-status/cook_board.svg) | Board of Commissioners |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/cook_pubhealth.svg) | Department of Public Health |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/cook_electoral.svg) | Electoral Board |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/cook_county.svg) | Government |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/cook_hospitals.svg) | Health and Hospitals System |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/cook_landbank.svg) | Land Bank |

### Illinois

| Status / Last Ran | Scraper |
|---------|--------|
| ![Status](https://s3.amazonaws.com/city-scrapers-status/il_labor.svg) | Illinois Labor Relations Board |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/metra_board.svg) | Metra Board of Directors |
| ![Status](https://s3.amazonaws.com/city-scrapers-status/regionaltransit.svg) | Regional Transportation Authority |

## Support this work

This project is organized and maintained by [City Bureau](http://www.citybureau.org/) and [ProPublica Illinois](https://www.propublica.org/illinois).

* [City Bureau](https://www.citybureau.org/)
  * [Donate](https://www.citybureau.org/press-club)
  * [Subscribe](https://citybureau.squarespace.com/newsletter/)
  * [Twitter @city_bureau](https://twitter.com/city_bureau/)
  * [Facebook](https://www.facebook.com/CityBureau/)
* [ProPublica Illinois](https://www.propublica.org/illinois)
  * [Donate](https://www.propublica.org/donate-illinois)
  * [Subscribe](http://go.propublica.org/sign-up)
  * [Twitter @propublicail](https://twitter.com/ProPublicaIL)
  * [Facebook](https://www.facebook.com/propublicaillinois/)
