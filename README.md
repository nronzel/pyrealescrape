# realescrape
Realescrape is a listing scraper for Realtor.com

Uses Requests & BeautifulSoup4.

> PLEASE NOTE: This is for educational purposes only and all data is publicly visible and available on the website without an account. The data being scraped is not monetized in any way.

## Description

Currently allows searching location. You can search using the following case-sensitive formats:
`Tampa_FL`
`Hillsborough-County_FL`
`33604`

I intend to sanitize the inputs and automatically form the input into the proper format.

The Beds, Baths, Type, Min Price, and Min Age are all currently fixed to the following values:
- `beds`: minimum 1 bedroom
- `baths`: minimum 1 bathroom
- `type`: single family homes only
- `min price`: $100_000 | this is to prevent listings with no price or 1$ listings
- `min age`: at least 3 years old. I may change this to 1 year, but it prevents new construction that isn't complete yet.

These values will be stored in variables and set by user input at some point, I would just like other functionality such as a proper database
and address parsing to be complete first.

## Coming Soon
- custom parameters - Location is now user input
- output to MongoDB or CSV
- Parse the address into separate categories to normalize. This will also
allow filtering by excluding towns or zip codes you don't like.


