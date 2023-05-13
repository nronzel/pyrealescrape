import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import logging

logging.basicConfig(level=logging.INFO)

BASE_URL = "https://www.realtor.com/realestateandhomes-search/"
STUB = "Hillsborough-County_FL/type-single-family-home/price-100000-na/age-3/sby-6/"
URL = BASE_URL + STUB
PAGES = 5
AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0"


def getSoup(URL):
    headers = {
        "user-agent": AGENT
    }
    try:
        page = requests.get(URL, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")
        return soup
    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException: {e}")
        return None


def get_home_data(house):
    data = house.find("div", class_="property-wrap")
    price = data.span.text.replace("$", "")
    beds = data.find("li", attrs={"data-label": "pc-meta-beds"}).span.text
    baths = data.find("li", attrs={"data-label": "pc-meta-baths"}).span.text
    sqft = data.find("li", attrs={"data-label": "pc-meta-sqft"}).span.text
    try:
        lotsize = data.find("li", attrs={"data-label": "pc-meta-sqftlot"}).text
    except AttributeError:
        lotsize = "-"
    address = data.find("div", attrs={"data-label": "pc-address"}).text
    link = house.find("div", class_="photo-wrap").a["href"]

    return {
        "PRICE $": price,
        "BEDS": beds,
        "BATHS": baths,
        "SQFT": sqft,
        "LOTSIZE": lotsize,
        "ADDRESS": address,
        "LINK": f"https://www.realtor.com{link}",
    }


def parseSoup(URL):
    soup = getSoup(URL)
    if soup is None:  # If there was an error getting the page
        return []
    homes = []
    for house in soup.find_all("li", attrs={"data-testid": "result-card"}):
        homes.append(get_home_data(house))
    return homes


def scrapeIt():
    all_homes = []
    for i in range(1, PAGES):
        URL = BASE_URL + STUB + f"pg-{i}"
        all_homes += parseSoup(URL)
        logging.info(f"Scraped: {URL}")
        time.sleep(2)

    return all_homes


def sendIt():
    homes = scrapeIt()
    df = pd.DataFrame(homes)
    df.to_csv("homes.csv", index=False)
    logging.info(df)


if __name__ == "__main__":
    sendIt()
