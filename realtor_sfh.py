import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import logging
import house_to_yard as hy
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)

HOME_TYPE = "type-single-family-home"
PAGES = 5
MIN_PRICE = "price-100000-na"

LOCATION = input("Location (e.g. Miami FL, 90210): ").replace(" ", "_").strip()
BASE_URL = "https://www.realtor.com/realestateandhomes-search/"
OPTIONS = (
    f"{LOCATION}/beds-1/baths-1/{HOME_TYPE}/{MIN_PRICE}/age-3+/pnd-hide/55p-hide/sby-6/"
)

URL = BASE_URL + OPTIONS
AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0"


def getSoup(URL):
    headers = {"user-agent": AGENT}
    try:
        page = requests.get(URL, headers=headers)
        if page.status_code != 200:
            logging.error(f"Request returned status code {page.status_code}")
            raise requests.exceptions.HTTPError(
                f"HTTPError: Received status code {page.status_code}"
            )
        soup = BeautifulSoup(page.content, "html.parser")
        return soup
    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException: {e}")
        return None


def extract_text(data, attr, default="-"):
    element = data.find("li", attrs={"data-label": attr})
    return element.span.text if element else default


def getHomeData(house):
    data = house.find("div", class_="property-wrap")
    price = data.span.text.replace("$", "")
    beds = extract_text(data, "pc-meta-beds")
    baths = extract_text(data, "pc-meta-baths")

    try:
        sqft = extract_text(data, "pc-meta-sqft").replace(",", "")
    except AttributeError:
        sqft = "-"

    try:
        lotsize = data.find("li", attrs={"data-label": "pc-meta-sqftlot"}).text
        size = hy.parse_lot_size(lotsize) if lotsize != "-" else "-"
    except AttributeError:
        lotsize = "-"
        size = "-"

    try:
        address = data.find("div", attrs={"data-label": "pc-address"}).text
        address_parts = address.split(",")
        if len(address_parts) != 3:
            raise ValueError("Address format is incorrect")
        street = address_parts[0].strip()
        city = address_parts[1].strip()
        state_zip = address_parts[2].split()
        if len(state_zip) != 2:
            raise ValueError("State and ZIP format is incorrect")
        state = state_zip[0].strip()
        zip_code = state_zip[1].strip()
    except (AttributeError, ValueError):
        street, city, state, zip_code = "-", "-", "-", "-"

    link = house.find("div", class_="photo-wrap").a["href"]

    hty_ratio = "-"
    house_ratio = "-"

    if size != "-" and sqft != "-" and size != 0:
        hty_ratio = round(int(size) / int(sqft), 2)
        house_ratio = round(int(sqft) / int(size), 2)

    return {
        "PRICE $": price,
        "BEDS": int(beds),
        "BATHS": int(baths.replace("+", "")),
        "SQFT": int(sqft.replace(",", "")) if sqft != "-" else "-",
        "LOTSIZE": int(hy.split_lot_size(lotsize)[0]),
        "LOTUNIT": hy.split_lot_size(lotsize)[1],
        "SIZE": size,
        "HtY": hty_ratio or "-",
        "HtY %": house_ratio or "-",
        "STREET": street,
        "CITY/TOWN": city,
        "STATE": state,
        "ZIP": int(zip_code),
        "LINK": f"https://www.realtor.com{link}",
    }


def parseSoup(URL):
    try:
        soup = getSoup(URL)
        if soup is None:
            return None
        homes = []
        house_elements = soup.find_all("li", attrs={"data-testid": "result-card"})
        if not house_elements:
            logging.warning(f"No house elements found at URL: {URL}")
            return None
        for house in house_elements:
            home_data = getHomeData(house)
            if home_data is not None:
                homes.append(home_data)
            else:
                logging.error(f"Error when parsing house data at URL: {URL}")
        return homes
    except requests.exceptions.HTTPError:
        return None


def scrapeIt():
    all_homes = []
    for i in range(1, PAGES + 1):
        URL = BASE_URL + OPTIONS + f"pg-{i}"
        new_homes = parseSoup(URL)
        if new_homes is None:
            logging.error("Stopping due to non 200 response.")
            break
        all_homes += new_homes
        logging.info(f"Scraped: {URL}")
        time.sleep(3)
    return all_homes


def sendIt():
    homes = scrapeIt()
    if homes:
        # open MongoDB connection on default port
        client = MongoClient('mongodb://localhost:27017')
        db = client['homedatabase']
        collection = db['homes']

        # create a dataframe and export to CSV
        df = pd.DataFrame(homes)
        df.to_csv(f"scans/{LOCATION}.csv", index=False)

        # create dict from the dataframe and insert into the DB
        data_dict = df.to_dict("records")
        collection.insert_many(data_dict)

        logging.info(df)
    else:
        logging.error("No home data scraped.")


if __name__ == "__main__":
    sendIt()
