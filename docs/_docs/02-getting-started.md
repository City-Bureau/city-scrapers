---
title: "Getting Started"
permalink: /docs/getting-started/
excerpt: "Intro to City Scrapers"
last_modified_at: 2018-10-04T20:15:56-04:00
toc: true
---

## Review your state's Open Meetings Act (OMA)

Each state has its own Open Meetings Act. With reasonable exceptions, all public bodies are required to hold meetings open to public and to give adequate notice of when these meetings are held. It's a good idea to familiarize yourself with your state's open meetings laws and Ballotpedia's state-by-state [list](https://ballotpedia.org/State_open_meetings_laws) is a great place to start.

## Define your local agency map

We focused our universe of meetings on the local- and county-level, at agencies like the City Council, Board of Education, Police Board, Metropolitan Water Reclamation District and the Regional Transportation Authority and their attendant boards, commissions, committees, sub-committees and advisory boards.

- Examples of governmental agencies that typically hold public meetings:

  - City Council
  - Board of Education
  - Police Board

- Types of meeting-holding bodies

  - Boards
  - Commissions
  - Committees
  - Sub-committees
  - Advisory boards

### Finding agencies

It can be challenging to find all of the different appointed bodies in an area, but there are a few approaches that have worked for us:

- See if your area includes a list of appointed bodies like [Chicago's directory](https://webapps1.chicago.gov/moboco/){:target="\_blank"} or the [Boards and Commissions site in Cuyahoga County](http://bc.cuyahogacounty.us/){:target="\_blank"}.
- Check the website of your local municipal or county government for any appointments that required legislative approval. The body for the appointment will be listed and can help find agencies not listed in other locations.
- Find your local code of ordinances (or an equivalent) usually hosted through companies like Municode or American Legal Publishing. Many agencies are described in these ordinances like in [Akron's municipal code](https://library.municode.com/oh/akron/codes/code_of_ordinances?nodeId=TIT3AD_CH31DEBOCO){:target="\_blank"}.

## Web Scrapers

Given the amount of different agencies we wanted to pull information from, we realized early on that checking each agency website manually would take too much time to be sustainable. By looking at patterns in how each website lists its meetings, we can write small programs that visit these web pages and follow custom rules to pull information for each site. This process is called [web scraping](https://en.wikipedia.org/wiki/Web_scraping){:target="\_blank"}, and we saved time by using freely available open source libraries like [Scrapy](https://scrapy.org/){:target="\_blank"} as a foundation for our code.

## GitHub and Open Source

Our project is on GitHub at [City-Bureau/city-scrapers](https://github.com/City-Bureau/city-scrapers/){:target="\_blank"} which makes it easier to manage tasks and lowers the barrier to entry for new contributors.

[GitHub](https://github.com/){:target="\_blank"} is a web application for managing software projects with functionality for organizing tasks, project documentation, and onboarding. Through our [GitHub issues](https://github.com/City-Bureau/city-scrapers/issues/){:target="\_blank"} we can track the status of work and assign scrapers or other issues to anyone who expresses interest. It also has tools for deploying updates to the code, reviewing submitted work, and publishing static HTML sites (including this one).

We also made the project open source, which for our specific license means all of the code we've written is available for others to copy and modify so long as they attribute the original creation to us. You can learn more about different options for open source software licenses at [choosealicense.com](https://choosealicense.com/){:target="\_blank"}.

## Templates

Before you start building scrapers, organize the information of your relevant agencies in a spreadsheet (you can start from our [downloadable template](https://docs.google.com/spreadsheets/d/1egRcdp5JPnRjk04gvNA-DrGP7TJg01hvPlDPnkjYCa0/edit#gid=1059508700){:target="\_blank"} or see our [example spreadsheet](https://docs.google.com/spreadsheets/d/1egRcdp5JPnRjk04gvNA-DrGP7TJg01hvPlDPnkjYCa0/edit#gid=0){:target="\_blank"}). Because we aimed to create a public-facing tool, we collected information like agency name, meeting-holding body name, jurisdiction, official website, topical tags, contact information and social media handles. As we began coding we added fields to track progress of each scraper.

![Google Sheets example](/assets/images/google_sheets.png "Google Sheets example"){:target="\_blank"}

## Best Practices

Get a sense of how meeting-holding bodies are scheduling public meetings. Do any agencies use a management tool like [Legistar](https://chicago.legistar.com/Calendar.aspx){:target="\_blank"} or [Municode](https://library.municode.com/il/cook_county){:target="\_blank"} that will be easier to scrape data from? Are any meeting dates stored in formats that are particularly difficult to access, such as in a PDF? If so, call the agency out on it! Given specific, structured feedback on how they could make their calendars more accessible, the public officials we met with were typically willing to do so. What's more, it may save some work on your end. Check out our best practices guides for [event managers](/assets/pdf/PublicMeetingsBestPractices.pdf){:target="\_blank"} and [technical managers](/assets/pdf/PublicMeetingsBestPractices.pdf){:target="\_blank"} to get started.
