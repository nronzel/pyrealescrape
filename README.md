# realescrape

Realescrape is a listing scraper for Realtor.com

Dependencies:
Python 3.10.6
Requests, BeautifulSoup4, Pandas, PyMongo
MongoDB instance running locally on default port (27017)

> PLEASE NOTE: This is for educational purposes only and all data is publicly visible and available on the website without an account. The data being scraped is not monetized in any way, and absolutely no images are scraped.

I fully expect this to break often and will try my best to keep it up to date.
I tried using `data-testid` selectors as much as possible in the hopes it doesn't
change as often as a dynamically generated class name would.

## Description

Currently allows searching location. You can search using the following case-sensitive formats:
`Tampa FL`
`Hillsborough-County FL`
`33604`

I intend to sanitize the inputs and automatically form the input into the proper format.

The Beds, Baths, Type, Min Price, and Min Age are all currently fixed to the following values:

- `beds`: minimum 1 bedroom
- `baths`: minimum 1 bathroom
- `type`: single family homes only
- `min price`: $100_000 | this is to prevent listings with no price or 1$ listings
- `min age`: at least 3 years old. I may change this to 1 year, but it
prevents new construction that isn't complete yet.

## Usage

-- to be filled out --

## Coming Soon

- custom parameters - Location is now user input
    - ~location~
    - beds
    - baths
    - single or multi family
- ~output to MongoDB and CSV~
- potentially rewrite in Go
- ~Parse the address into separate categories to normalize. This will also
  allow filtering by excluding towns or zip codes you don't like.~
- rotating user-agents
- implementing a proxy and rotating proxies to help prevent rate-limiting

## Goals and Lessons

My goal for this project is to have a frontend written in SolidJS, data
stored in MongoDB, and served through an Express API.

I DO NOT intend on setting up public hosting for this due to how easily it will break,
and legality issues regarding others' intentions with the data.

As I stated above, this is for educational purposes only. I see this as a
great opportunity to learn some backend programming, brush up on my Python,
and build out a full stack application.

Instructions will be provided in this readme once it is complete so you can
install and host it locally and play around with it yourself.

My original intention was to use some form of real estate API and create a
public site one could use to browse homes as a real estate investor.

However, I found it quite difficult to find any free, or even cheap, public
real estate APIs. I resorted to writing this scraper and instead saw it as a
good opportunity to learn new concepts.

## Troubleshooting

As scrapers inevitably will break, you can open an issue to address
it or fork this project and submit a pull request with your fixes.

I will try to keep up with the selectors breaking as much as possible.
